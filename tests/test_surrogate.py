
import pytest
import numpy as np
from MannKS._surrogate import surrogate_test, _iaaft_surrogates, _lomb_scargle_surrogates
from MannKS.trend_test import trend_test

try:
    import astropy
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

def test_iaaft_null_case():
    """Test IAAFT on pure random noise (should find no trend relative to null)."""
    rng = np.random.default_rng(42)
    n = 100
    x = rng.standard_normal(n)
    t = np.arange(n)

    # IAAFT requires even spacing, which we have
    res = surrogate_test(x, t, method='iaaft', n_surrogates=200, random_state=42)

    # The original score should be within the distribution of surrogate scores
    # i.e., p-value should be high (not significant)
    assert res.p_value > 0.05
    assert not res.trend_significant
    assert res.method == 'iaaft'

def test_iaaft_trend_case():
    """Test IAAFT on strong trend (should be significant)."""
    rng = np.random.default_rng(42)
    n = 100
    t = np.arange(n)
    x = 0.1 * t + rng.standard_normal(n) # Strong trend

    res = surrogate_test(x, t, method='iaaft', n_surrogates=200, random_state=42)

    # Should be significant
    assert res.p_value < 0.05
    assert res.trend_significant

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_lomb_scargle_null_irregular():
    """Test Lomb-Scargle on unevenly sampled noise."""
    rng = np.random.default_rng(42)
    n = 100
    t = np.sort(rng.uniform(0, 200, n)) # Irregular time
    x = rng.standard_normal(n)

    res = surrogate_test(x, t, method='lomb_scargle', n_surrogates=200, random_state=42)

    assert res.p_value > 0.05
    assert not res.trend_significant
    assert res.method == 'lomb_scargle'

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_lomb_scargle_trend_irregular():
    """Test Lomb-Scargle on unevenly sampled trend."""
    rng = np.random.default_rng(42)
    n = 100
    t = np.sort(rng.uniform(0, 200, n))
    x = 0.05 * t + rng.standard_normal(n)

    res = surrogate_test(x, t, method='lomb_scargle', n_surrogates=200, random_state=42)

    assert res.p_value < 0.05
    assert res.trend_significant

def test_auto_selection():
    """Test automatic method selection based on sampling."""
    rng = np.random.default_rng(42)

    # Even
    t_even = np.arange(50)
    x = rng.standard_normal(50)
    res_even = surrogate_test(x, t_even, method='auto', n_surrogates=10)
    assert res_even.method == 'iaaft'

    # Uneven
    t_uneven = np.sort(rng.uniform(0, 100, 50))
    # Ensure it's strictly uneven
    t_uneven[1] += 0.1

    if HAS_ASTROPY:
        res_uneven = surrogate_test(x, t_uneven, method='auto', n_surrogates=10)
        assert res_uneven.method == 'lomb_scargle'
    else:
        # Fallback behavior
        with pytest.warns(UserWarning, match="Uneven sampling detected"):
            res_uneven = surrogate_test(x, t_uneven, method='auto', n_surrogates=10)
        assert res_uneven.method == 'iaaft'

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_advanced_params():
    """Test passing advanced parameters to Lomb-Scargle."""
    rng = np.random.default_rng(42)
    n = 50
    t = np.sort(rng.uniform(0, 100, n))
    x = rng.standard_normal(n)
    dy = np.ones(n) * 0.1

    # Should run without error
    res = surrogate_test(
        x, t, dy=dy,
        method='lomb_scargle',
        n_surrogates=10,
        freq_method='log',
        normalization='psd',
        fit_mean=False
    )
    assert res.method == 'lomb_scargle'
    assert len(res.surrogate_scores) == 10

def test_trend_test_integration():
    """Verify integration of surrogate_test into trend_test."""
    rng = np.random.default_rng(42)
    n = 50
    t = np.arange(n)
    x = rng.standard_normal(n)

    # Run trend_test with surrogate_method
    res = trend_test(x, t, surrogate_method='iaaft', n_surrogates=10, random_state=42)

    assert res.surrogate_result is not None
    assert res.surrogate_result.method == 'iaaft'
    assert res.surrogate_result.n_surrogates == 10

    # Check default is none
    res_def = trend_test(x, t)
    assert res_def.surrogate_result is None

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_trend_test_integration_advanced():
    """Verify advanced params via trend_test."""
    rng = np.random.default_rng(42)
    n = 50
    t = np.sort(rng.uniform(0, 100, n))
    x = rng.standard_normal(n)

    res = trend_test(
        x, t,
        surrogate_method='lomb_scargle',
        n_surrogates=10,
        surrogate_kwargs={'normalization': 'psd'},
        random_state=42
    )

    assert res.surrogate_result is not None
    assert res.surrogate_result.method == 'lomb_scargle'
