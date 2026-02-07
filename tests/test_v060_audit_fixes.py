
import pytest
import numpy as np
import pandas as pd
import warnings
from unittest.mock import patch, MagicMock
from MannKS.power import power_test
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS._surrogate import surrogate_test

def test_trend_test_surrogate_kwargs_median_aggregation_error():
    """
    Test that trend_test raises ValueError when using median aggregation
    and passing array-like surrogate_kwargs (misalignment risk).
    """
    n = 100
    t = pd.date_range(start='2000-01-01', periods=n, freq='D')
    x = np.random.randn(n)
    dy = np.random.rand(n) * 0.1

    # Median aggregation loses original index
    with pytest.raises(ValueError, match="Surrogate argument .* cannot be automatically mapped"):
        trend_test(
            x, t,
            agg_method='median',
            agg_period='month',
            surrogate_method='iaaft',
            n_surrogates=10,
            surrogate_kwargs={'dy': dy} # Array-like argument matching original length
        )

def test_trend_test_surrogate_kwargs_middle_aggregation_success():
    """
    Test that trend_test works when using middle aggregation
    and passing array-like surrogate_kwargs (index preserved).
    """
    n = 100
    t = pd.date_range(start='2000-01-01', periods=n, freq='D')
    x = np.random.randn(n)
    dy = np.random.rand(n) * 0.1

    # Middle aggregation keeps original index
    try:
        trend_test(
            x, t,
            agg_method='middle',
            agg_period='month',
            surrogate_method='iaaft', # Use iaaft for speed/simplicity
            n_surrogates=10,
            surrogate_kwargs={'dy': dy}
        )
    except ValueError as e:
        pytest.fail(f"trend_test raised ValueError unexpectedly for agg_method='middle': {e}")

def test_seasonal_trend_test_surrogate_aggregation():
    """
    Verify that seasonal_trend_test aggregates surrogate scores correctly.
    We mock surrogate_test to return deterministic scores and check the sum.
    """
    n_years = 3
    t = pd.date_range(start='2000-01-01', periods=n_years*12, freq='ME')
    x = np.random.randn(len(t))

    n_surrogates = 5
    fixed_scores = np.ones(n_surrogates) # Each season returns [1, 1, 1, 1, 1]

    # Mock return value of surrogate_test
    mock_result = MagicMock()
    mock_result.surrogate_scores = fixed_scores
    mock_result.notes = []
    mock_result.p_value = 0.5

    with patch('MannKS.seasonal_trend_test.surrogate_test', return_value=mock_result) as mock_surr:
        res = seasonal_trend_test(
            x, t,
            period=12,
            season_type='month',
            surrogate_method='iaaft',
            n_surrogates=n_surrogates
        )

        # We expect 12 seasons.
        # Total surrogate score should be sum of scores from each season.
        # Since each season returns [1, 1, ...], and there are 12 seasons with data,
        # result should be [12, 12, ...]

        expected_total = fixed_scores * 12
        np.testing.assert_array_almost_equal(res.surrogate_result.surrogate_scores, expected_total)
        assert mock_surr.call_count == 12

def test_power_test_slope_scaling():
    """
    Verify slope scaling logic in power_test.
    If we provide slope=1/year, it should be converted to ~3.17e-8 / sec.
    """
    x = np.random.randn(100)
    t = np.arange(100) * 86400 # Daily data in seconds
    slopes = [365.25 * 86400] # 1 unit per year (if scaling='year')

    # We'll mock _lomb_scargle_surrogates to return zeros so x_sim = beta * t
    with patch('MannKS.power._lomb_scargle_surrogates', return_value=np.zeros((1, 100))):
        with patch('MannKS.power.surrogate_test') as mock_test:
            # Mock return
            mock_test.return_value = MagicMock(p_value=0.0)

            power_test(
                x, t,
                slopes=slopes,
                slope_scaling='year',
                n_simulations=1,
                n_surrogates=10,
                surrogate_method='lomb_scargle'
            )

            # Check the first call argument 'x' passed to surrogate_test
            # args[0] is x_sim
            call_args = mock_test.call_args
            x_sim_passed = call_args[0][0]

            # Expected: x_sim = 0 + 1.0 * (t - t.mean())
            # beta = (365.25*86400) / (365.25*86400) = 1.0
            t_centered = t - np.mean(t)
            expected = 1.0 * t_centered

            np.testing.assert_array_almost_equal(x_sim_passed, expected)

def test_power_test_suppresses_warnings():
    """
    Verify that power_test does NOT suppress unknown UserWarnings from surrogate_test.
    But it SHOULD suppress 'Censored data...' warnings.
    """
    x = np.random.randn(10)
    t = np.arange(10)
    slopes = [0.1]

    def warn_surrogate(*args, **kwargs):
        warnings.warn("Performance Warning", UserWarning)
        warnings.warn("Censored data detected in surrogate test", UserWarning)
        return MagicMock(p_value=0.5)

    with patch('MannKS.power._lomb_scargle_surrogates', return_value=np.zeros((1, 10))):
        with patch('MannKS.power.surrogate_test', side_effect=warn_surrogate):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                power_test(
                    x, t, slopes=slopes, n_simulations=1, n_surrogates=10,
                    surrogate_method='lomb_scargle'
                )

                # Unknown warning should bubble up
                perf_warnings = [str(warn.message) for warn in w if "Performance Warning" in str(warn.message)]
                assert len(perf_warnings) > 0, "Unknown warning should NOT be suppressed"

                # Censored warning should be suppressed
                censored_warnings = [str(warn.message) for warn in w if "Censored data detected" in str(warn.message)]
                assert len(censored_warnings) == 0, "Known nuisance warning SHOULD be suppressed"

def test_power_test_warns_on_complexity():
    """
    Verify that power_test triggers a warning if total complexity is high.
    We'll set inputs to exceed the threshold (which we'll define as 10M ops).
    """
    # N=1000, n_sim=10, n_surr=100, n_slopes=10 -> 1M.
    # We need > 10M.
    # N=10000. 10000 * 10 * 100 * 10 = 100M.

    x = np.random.randn(10000)
    t = np.arange(10000)
    slopes = [0.1] * 10 # 10 slopes

    # We mock execution so it doesn't actually run
    with patch('MannKS.power._lomb_scargle_surrogates', return_value=np.zeros((10, 10000))):
        with patch('MannKS.power.surrogate_test', return_value=MagicMock(p_value=0.5)):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                power_test(
                    x, t, slopes=slopes,
                    n_simulations=10,
                    n_surrogates=100,
                    surrogate_method='lomb_scargle' # Must be LS to trigger warning
                )

                # Check for "computationally expensive" warning
                relevant = [str(warn.message) for warn in w if "computationally expensive" in str(warn.message)]
                assert len(relevant) > 0, "Should warn about complexity"

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main(["-v", __file__]))
