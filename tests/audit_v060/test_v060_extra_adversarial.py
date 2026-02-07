
import pytest
import numpy as np
import pandas as pd
import warnings
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.power import power_test
from MannKS._surrogate import surrogate_test

def test_surrogate_constant_input():
    """Test surrogate generation on constant input data."""
    x = np.ones(20)
    t = np.arange(20)

    # Test Lomb-Scargle (requires astropy)
    try:
        res_ls = surrogate_test(x, t, method='lomb_scargle', n_surrogates=10)
        # Surrogates of constant should be constant
        assert np.allclose(res_ls.surrogate_scores, 0, atol=1e-5)
        # Original score of constant is 0
        assert res_ls.original_score == 0
    except ImportError:
        pytest.skip("Astropy not installed")

    # Test IAAFT
    res_iaaft = surrogate_test(x, t, method='iaaft', n_surrogates=10)
    # IAAFT on constant input should also be constant
    assert np.allclose(res_iaaft.surrogate_scores, 0, atol=1e-5)

def test_surrogate_small_n():
    """Test surrogate test with very small n_surrogates (p-value check)."""
    x = np.random.randn(20)
    t = np.arange(20)

    # n=5 implies min p-value = 1/6 = 0.166 > 0.05
    res = surrogate_test(x, t, n_surrogates=5)

    # Check that p-value is correctly calculated
    expected_min_p = 1/6
    assert res.p_value >= expected_min_p

def test_trend_test_aggregation_mismatch_error_message():
    """Verify exact error message for mismatched kwargs in trend_test."""
    n = 100
    t = pd.date_range("2020-01-01", periods=n, freq="D")
    x = np.random.randn(n)
    dy = np.ones(n) * 0.1

    # Check singular/plural message
    with pytest.raises(ValueError, match="Surrogate argument 'dy'"):
        trend_test(
            x, t,
            agg_method='median', agg_period='month',
            surrogate_method='lomb_scargle',
            surrogate_kwargs={'dy': dy}
        )

def test_seasonal_trend_test_aggregation_mismatch_error_message():
    """Verify exact error message for mismatched kwargs in seasonal_trend_test."""
    # Create 2 years of monthly data (24 points)
    n = 24
    t = pd.date_range("2020-01-01", periods=n, freq="ME")
    x = np.random.randn(n)

    # Use aggregation that destroys index mapping: 'median'
    # We use daily data and aggregate to monthly

    n_days = 60
    t_days = pd.date_range("2020-01-01", periods=n_days, freq="D")
    x_days = np.random.randn(n_days)
    dy_days = np.ones(n_days)

    # Check singular/plural message for seasonal test
    with pytest.raises(ValueError, match="Surrogate arguments .* cannot be automatically mapped"):
        seasonal_trend_test(
            x_days, t_days,
            season_type='month',
            agg_method='median', # Destroys original_index
            surrogate_method='lomb_scargle',
            surrogate_kwargs={'dy': dy_days}
        )

def test_power_test_censored_warning():
    """Test if power_test warns about censored data interpretation."""
    x = np.random.randn(20)
    t = np.arange(20)
    censored = np.zeros(20, dtype=bool)
    censored[0] = True # One censored point

    # power_test suppresses "Censored data detected" warning.
    # We check if it raises any OTHER warning or if suppression works.

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always") # Cause all warnings to be caught
        res = power_test(
            x, t, [0.1],
            n_simulations=5, n_surrogates=10,
            surrogate_kwargs={'censored': censored}
        )

        # Check that we didn't get the "Censored data detected" warning (it should be suppressed)
        censored_warnings = [str(w.message) for w in record if "Censored data detected" in str(w.message)]
        assert len(censored_warnings) == 0

def test_lomb_scargle_stability_near_constant():
    """Test numerical stability of Lomb-Scargle surrogates on near-constant data."""
    # Data with extremely low variance
    x = np.ones(20) + np.random.randn(20) * 1e-10
    t = np.arange(20)

    # Should not crash or produce NaNs
    try:
        res = surrogate_test(x, t, method='lomb_scargle', n_surrogates=10)
        assert not np.any(np.isnan(res.surrogate_scores))
    except ImportError:
        pytest.skip("Astropy not installed")
