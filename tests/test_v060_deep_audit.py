
import pytest
import numpy as np
import pandas as pd
import warnings
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.power import power_test
from MannKS._surrogate import surrogate_test

def test_surrogate_kwargs_misalignment_with_aggregation():
    """
    Test that providing raw-length surrogate kwargs (e.g. error bars)
    when using aggregation raises a clear ValueError, because index mapping is lost.

    This verifies existing safety logic in trend_test.py (v0.6.0 audit requirement).
    """
    n = 100
    t = pd.date_range("2020-01-01", periods=n, freq="D")
    x = np.random.randn(n)
    dy = np.ones(n) * 0.1

    # Aggregation enabled -> length changes, original_index lost
    # We pass 'dy' matching original length
    with pytest.raises(ValueError, match="Surrogate argument .* cannot be automatically mapped"):
        trend_test(
            x, t,
            agg_method='median', agg_period='month',
            surrogate_method='lomb_scargle',
            surrogate_kwargs={'dy': dy}
        )

def test_seasonal_surrogate_kwargs_misalignment():
    """
    Same check for seasonal trend test.
    Verifies existing safety logic in seasonal_trend_test.py for aggregation scenarios.
    """
    # We need multiple obs per season to force aggregation and loss of original_index.
    # AND we need >1 aggregated point per season to trigger the trend test loop where the check lives.
    # So we need multiple years.
    n = 365 * 3 # 3 years
    t = pd.date_range("2020-01-01", periods=n, freq="D")
    x = np.random.randn(n)
    dy = np.ones(n) * 0.1

    # Aggregation enabled (use 'median' to ensure original_index is lost)
    # Aggregating daily data to monthly seasons (resulting in ~3 points per season)
    with pytest.raises(ValueError, match="Surrogate arguments .* cannot be automatically mapped"):
        seasonal_trend_test(
            x, t,
            season_type='month',
            agg_method='median',
            surrogate_method='lomb_scargle',
            surrogate_kwargs={'dy': dy}
        )

def test_power_test_minimal_data():
    """Test power_test with minimal data (n=3) to ensure no crashes."""
    x = [1, 2, 3]
    t = [1, 2, 3]
    slopes = [0.1, 0.5]

    # Minimal run
    res = power_test(
        x, t, slopes,
        n_simulations=5,
        n_surrogates=20,
        surrogate_method='iaaft'
    )
    assert len(res.power) == 2
    assert not np.any(np.isnan(res.power))

def test_lomb_scargle_constant_data():
    """
    Test Lomb-Scargle surrogates with constant data.
    Should handle zero variance gracefully (or raise specific error),
    not crash with mysterious numpy warnings.
    """
    x = np.ones(50)
    t = np.arange(50)

    # This might trigger the divide by zero warning seen in logs
    # We want to see if it finishes or crashes
    res = surrogate_test(
        x, t,
        method='lomb_scargle',
        n_surrogates=10
    )
    # If constant, S-statistic should be 0. Surrogates also constant?
    # Or noise?
    # Lomb-Scargle on constant data: Power is 0.
    # Synthesis from 0 power -> 0 amplitude -> Constant 0 surrogates?
    # Or floating point noise?

    assert res.original_score == 0
    # Surrogates should effectively imply no trend
    assert not res.trend_significant
    # Check that p-value is valid (likely 1.0 or similar)
    assert 0 <= res.p_value <= 1

def test_surrogate_zero_surrogates():
    """Test surrogate_test with n_surrogates=0 or negative."""
    x = np.random.randn(20)
    t = np.arange(20)

    # Should raise ValueError
    with pytest.raises(ValueError, match="n_surrogates.*must be positive"):
        surrogate_test(x, t, method='iaaft', n_surrogates=0)

def test_seasonal_missing_season():
    """Test seasonal trend test where one season is completely missing in data."""
    # 2 years, missing 'February' in both years
    t = pd.to_datetime(['2020-01-15', '2020-03-15', '2021-01-15', '2021-03-15'])
    x = [1, 2, 3, 4]

    # Month seasonality. Feb (2) is missing.
    # Should run fine, just ignoring that season.
    res = seasonal_trend_test(
        x, t,
        season_type='month',
        surrogate_method='iaaft',
        n_surrogates=10
    )
    assert res.trend != 'error'

def test_power_test_nan_slopes():
    """Test power_test with NaN in slopes list."""
    x = np.random.randn(20)
    t = np.arange(20)
    slopes = [0.1, np.nan, 0.5]

    res = power_test(x, t, slopes, n_simulations=5, n_surrogates=20)

    # NaN slope injection: x + NaN * t = NaN.
    # surrogate_test on NaN data -> ?
    # Typically library filters NaNs. If all NaNs, throws error.

    # We expect the result for that slope to be valid (maybe 0 power) or NaN power.
    assert len(res.power) == 3
    # Check what happened to the NaN slope result
    nan_idx = 1
    # Likely the test ran on NaNs, resulting in errors or 0 detections
    # Ideally checking res.power[nan_idx]

def test_surrogate_memory_warning_check():
    """
    Verify the memory warning logic in _lomb_scargle_surrogates.
    """
    x = np.random.randn(10)
    t = np.arange(10)

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always") # Capture all
        surrogate_test(x, t, method='lomb_scargle', n_surrogates=10, max_iter=1)

        # Filter for the specific warning about performance
        relevant = [w for w in record if "computational" in str(w.message)]
        assert len(relevant) == 0
