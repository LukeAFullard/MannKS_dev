
import pytest
import numpy as np
import warnings
from MannKS.trend_test import trend_test
from MannKS._surrogate import surrogate_test

def test_constant_data_surrogate():
    """Constant data should return constant surrogates and valid stats (no crash)."""
    x = np.ones(100)
    t = np.arange(100)

    # IAAFT
    res = surrogate_test(x, t, method='iaaft', n_surrogates=10)
    assert np.all(res.surrogate_scores == 0) # No trend in surrogates
    assert res.original_score == 0 # No trend in data

    # Lomb-Scargle
    # Should handle constant data by returning copies or zero-variance result
    # without crashing in astropy
    try:
        from MannKS._surrogate import HAS_ASTROPY
        if HAS_ASTROPY:
            res_ls = surrogate_test(x, t, method='lomb_scargle', n_surrogates=10)
            assert np.all(res_ls.surrogate_scores == 0)
    except ImportError:
        pass

def test_nan_handling():
    """Surrogate test should fail or warn with NaNs if not pre-processed?
    Actually trend_test usually filters them. surrogate_test takes x, t arrays.
    """
    x = np.array([1, 2, np.nan, 4, 5])
    t = np.arange(5)

    # If passed directly to surrogate_test, what happens?
    # _mk_score... handles NaNs? Usually MannKS expects clean data or filters it.

    # Let's check trend_test integration, which does filtering.

    res = trend_test(x, t, surrogate_method='iaaft', n_surrogates=10)
    assert res.p is not None

def test_short_series():
    """Very short series."""
    x = np.array([1, 2, 3])
    t = np.arange(3)

    res = surrogate_test(x, t, method='iaaft', n_surrogates=10)
    # Should run
    assert len(res.surrogate_scores) == 10

def test_invalid_n_surrogates():
    x = np.arange(10)
    t = np.arange(10)
    with pytest.raises(ValueError, match="positive"):
        surrogate_test(x, t, n_surrogates=0)
    with pytest.raises(ValueError, match="positive"):
        surrogate_test(x, t, n_surrogates=-10)
