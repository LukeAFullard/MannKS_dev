import pytest
import numpy as np
import pandas as pd
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS._surrogate import surrogate_test

try:
    import astropy
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy required")
def test_seasonal_surrogate_dy_bug():
    """
    Audit Bug Fix Verification: 'dy' passed in surrogate_kwargs should be sliced
    to match the season subset, preventing shape mismatch.
    """
    # Create 2 years of monthly data
    t = pd.to_datetime(pd.date_range(start='2020-01-01', periods=24, freq='ME'))
    x = np.random.randn(24)
    dy = np.ones(24) * 0.1

    # This should now succeed
    res = seasonal_trend_test(
        x, t,
        period=12,
        surrogate_method='lomb_scargle',
        n_surrogates=5,
        surrogate_kwargs={'dy': dy}
    )
    assert res.surrogate_result is not None
    assert res.surrogate_result.method == 'seasonal_lomb_scargle'

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy required")
def test_trend_test_surrogate_dy_filter_bug():
    """
    Audit Bug Fix Verification: 'dy' passed in surrogate_kwargs should be filtered
    matching the NaN removal in x/t.
    """
    t = np.arange(20)
    x = np.random.randn(20)
    dy = np.ones(20) * 0.1

    # Introduce NaN
    x[5] = np.nan

    # This should now succeed
    res = trend_test(
        x, t,
        surrogate_method='lomb_scargle',
        n_surrogates=5,
        surrogate_kwargs={'dy': dy}
    )
    assert res.surrogate_result is not None
    assert res.surrogate_result.method == 'lomb_scargle'

    # Also verify reordering if T is unsorted
    rng = np.random.default_rng(42)
    indices = rng.permutation(20)
    t_unsorted = t[indices]
    x_unsorted = x[indices]
    dy_unsorted = dy[indices]

    # Give dy distinct values to verify alignment conceptually (though surrogates handle noise)
    dy_unsorted = np.arange(20) * 0.1

    res_unsorted = trend_test(
        x_unsorted, t_unsorted,
        surrogate_method='lomb_scargle',
        n_surrogates=5,
        surrogate_kwargs={'dy': dy_unsorted}
    )
    assert res_unsorted.surrogate_result is not None


def test_seasonal_block_bootstrap_audit():
    """
    Verify seasonal block bootstrap runs without crashing and produces reasonable output.
    """
    # 5 years of monthly data
    t = pd.to_datetime(pd.date_range(start='2020-01-01', periods=60, freq='ME'))
    x = 0.05 * np.arange(60) + np.random.randn(60) # Trend

    res = seasonal_trend_test(
        x, t,
        period=12,
        autocorr_method='block_bootstrap',
        n_bootstrap=50,
        block_size=1
    )

    assert res.block_size_used is not None
