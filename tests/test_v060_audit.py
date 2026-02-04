
import pytest
import numpy as np
import pandas as pd
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS._surrogate import surrogate_test

def test_audit_surrogate_aggregation_mismatch():
    """
    Test edge case: User requests aggregation AND surrogates AND provides kwargs (e.g. dy)
    that match original length.
    """
    # Create daily data for 2 years (730 points)
    n = 730
    t = pd.date_range(start='2020-01-01', periods=n, freq='D')
    x = np.random.randn(n) + np.linspace(0, 1, n)
    dy = np.ones(n) * 0.1 # Errors for Lomb-Scargle

    # Request aggregation to 'month' -> ~24 points
    # Request surrogate_method='lomb_scargle' which uses 'dy'
    # dy is length 730. x_agg is length 24.

    # This should arguably FAIL or WARN, but definitely not CRASH with opaque error.
    # Current implementation tries to slice dy.
    # If it fails to slice correctly, Astropy will raise ValueError due to shape mismatch.

    try:
        trend_test(
            x, t,
            agg_method='median',
            agg_period='month',
            surrogate_method='lomb_scargle',
            n_surrogates=10,
            surrogate_kwargs={'dy': dy}
        )
        pytest.fail("Should have raised ValueError for mismatched surrogate kwargs")
    except ValueError as e:
        # v0.6.0 Fix: Updated error message to be more explicit about aggregation
        assert "cannot be automatically mapped" in str(e)
    except Exception as e:
        pytest.fail(f"Aggregation + Surrogate + Kwargs crashed with unexpected error: {e}")

def test_audit_surrogate_kwargs_sanitization():
    """
    Ensure surrogate_kwargs cannot override critical parameters like 'method'.
    """
    x = np.random.randn(50)
    t = np.arange(50)

    # User tries to force 'iaaft' via kwargs while main arg is 'lomb_scargle'
    res = trend_test(
        x, t,
        surrogate_method='lomb_scargle',
        n_surrogates=10,
        surrogate_kwargs={'method': 'iaaft'}
    )

    assert res.surrogate_result.method == 'lomb_scargle'
    # Also check it didn't pass 'method' to _lomb_scargle_surrogates (which would accept **kwargs)
    # If it did, it might be harmless but good to verify.

def test_audit_seasonal_surrogate_aggregation_mismatch():
    """
    Same as above but for seasonal_trend_test.
    """
    # 5 years of monthly data (60 points)
    # Aggregated from daily data?
    n = 365 * 3
    t = pd.date_range(start='2020-01-01', periods=n, freq='D')
    x = np.random.randn(n)
    dy = np.ones(n) * 0.1

    # Aggregating to Month
    try:
        seasonal_trend_test(
            x, t,
            season_type='month',
            agg_method='median',
            surrogate_method='lomb_scargle',
            n_surrogates=5,
            surrogate_kwargs={'dy': dy}
        )
        pytest.fail("Should have raised ValueError for mismatched seasonal surrogate kwargs")
    except ValueError as e:
        assert "Automatic mapping is not possible" in str(e)
    except Exception as e:
        pytest.fail(f"Seasonal Aggregation + Surrogate + Kwargs crashed with unexpected error: {e}")

def test_audit_bootstrap_constant_data():
    """
    Block bootstrap on constant data should not crash.
    """
    x = np.ones(20)
    t = np.arange(20)

    res = trend_test(
        x, t,
        autocorr_method='block_bootstrap',
        n_bootstrap=50
    )

    assert res.p == 1.0 # Or near 1.0?
    assert res.s == 0
    assert res.var_s == 0 # Bootstrap distribution is all zeros

def test_audit_short_series_surrogate():
    """
    Very short series (N=4).
    """
    x = [1, 2, 3, 4]
    t = [1, 2, 3, 4]

    res = trend_test(
        x, t,
        surrogate_method='iaaft', # Should work even if short
        n_surrogates=10
    )
    assert res.trend != 'error'

def test_audit_unsorted_bootstrap():
    """
    Ensure unsorted input is handled correctly by block bootstrap.
    """
    x = np.array([1, 2, 3, 4, 5])
    t = np.array([1, 2, 3, 4, 5])

    # Shuffle
    idx = [0, 4, 1, 3, 2]
    x_shuf = x[idx]
    t_shuf = t[idx]

    res = trend_test(
        x_shuf, t_shuf,
        autocorr_method='block_bootstrap',
        n_bootstrap=50
    )

    # Should detect trend
    assert res.z > 0
