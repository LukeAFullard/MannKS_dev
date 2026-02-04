
import pytest
import numpy as np
import pandas as pd
import sys
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

@pytest.mark.skipif(not HAS_ASTROPY, reason="Astropy not installed")
def test_iterative_ls():
    """Test the iterative Lomb-Scargle feature."""
    rng = np.random.default_rng(42)
    n = 20
    t = np.sort(rng.uniform(0, 100, n))
    x = rng.standard_normal(n)

    # Should run without error
    res = surrogate_test(
        x, t,
        method='lomb_scargle',
        n_surrogates=2,
        max_iter=3, # Small iterations for speed
        random_state=42
    )
    assert res.method == 'lomb_scargle'
    assert len(res.surrogate_scores) == 2

def test_surrogate_kwargs_slicing(monkeypatch):
    """
    Verify that array-like surrogate_kwargs are sliced correctly when
    trend_test filters out NaNs from the input.
    """
    # Create data with NaNs
    n = 20
    x = np.random.randn(n)
    t = np.arange(n)
    x[5] = np.nan # Introduce NaN

    # Create an error array (dy) matching original length
    dy = np.ones(n) * 0.1
    dy[5] = 999 # Check if this outlier is removed

    # Access the module correctly
    tt_module = sys.modules['MannKS.trend_test']

    captured_kwargs = {}

    # Original function
    orig_surrogate = tt_module.surrogate_test

    def mock_surrogate_test(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return orig_surrogate(*args, **kwargs)

    monkeypatch.setattr(tt_module, 'surrogate_test', mock_surrogate_test)

    trend_test(
        x, t,
        surrogate_method='lomb_scargle',
        n_surrogates=10,
        surrogate_kwargs={'dy': dy}
    )

    assert 'dy' in captured_kwargs
    dy_received = captured_kwargs['dy']
    assert len(dy_received) == n - 1
    assert 999 not in dy_received

def test_censored_surrogate_propagation():
    """
    Verify that censoring flags are propagated to surrogates, reducing variance
    (conservative behavior removal) compared to imputation-only surrogates.
    """
    # Setup: censored data with overlap where imputation increases variance
    x_val = np.array([5.0, 2.0, 5.0, 3.0])
    censored = np.array([True, False, True, False]) # <5, 2, <5, 3
    cen_type = np.array(['lt', 'not', 'lt', 'not'])
    lt_mult = 0.5
    t = np.arange(4)

    # Run surrogate_test
    # This uses the new implementation (propagating censoring)
    res = surrogate_test(
        x_val, t, censored=censored, cen_type=cen_type,
        method='iaaft', n_surrogates=1000, random_state=42,
        lt_mult=lt_mult
    )

    std_surr = np.std(res.surrogate_scores)

    # From audit:
    # Imputed-only std was ~2.77
    # Censored-propagated std was ~2.24 (2.49 in sample)

    # We assert it is significantly below the imputation-only baseline
    assert std_surr < 2.65

def test_surrogate_kwargs_slicing_with_dataframe_and_nans():
    """
    Test that surrogate_kwargs are correctly sliced when input x is a DataFrame
    with NaNs and a DateTimeIndex, causing trend_test to filter data.
    """
    # Create data with NaNs
    dates = pd.date_range("2020-01-01", periods=10, freq="D")
    values = np.arange(10).astype(float)
    values[5] = np.nan # Introduce NaN at index 5

    df = pd.DataFrame({'value': values}, index=dates)

    # Create a kwargs array that matches original length
    # dy is commonly used in Lomb-Scargle
    dy = np.ones(10) * 0.1
    # We set index 5 to a sentinel value to check logic, but since it's filtered
    # we won't see it in the surrogate test call.

    # We also pass a dummy kwarg to see if it gets PASSED through without error now
    custom_arg = np.arange(10)

    try:
        if HAS_ASTROPY:
            method = 'lomb_scargle'
        else:
            method = 'iaaft' # Fallback for test environment without astropy (though requirements say it is there)

        result = trend_test(
            df, dates,
            surrogate_method=method,
            n_surrogates=10,
            surrogate_kwargs={'dy': dy, 'custom_arg': custom_arg}
        )
    except Exception as e:
        pytest.fail(f"trend_test raised exception: {e}")

    assert result.surrogate_result is not None
    assert result.surrogate_result.method == method

def test_surrogate_imputation_logic_consistency():
    """
    Check if surrogate test handles censoring by imputation consistent with expectations.
    """
    x = np.array([1, 2, 3, 4, 5], dtype=float)
    t = np.arange(5)
    censored = np.array([True, False, False, False, True]) # <1, 2, 3, 4, <5
    cen_type = np.array(['lt', 'not', 'not', 'not', 'lt'])

    res = surrogate_test(
        x, t,
        censored=censored,
        cen_type=cen_type,
        method='iaaft',
        n_surrogates=10,
        lt_mult=0.5
    )

    assert res.notes is not None
    # Note: The warning is captured by pytest, but notes are returned in result
    assert any("Censored data: surrogates generated from imputed values" in note for note in res.notes)
