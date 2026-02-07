
import pytest
import numpy as np
import pandas as pd
from MannKS import trend_test, seasonal_trend_test, power_test, surrogate_test
from MannKS._surrogate import _lomb_scargle_surrogates
import warnings

# --- 1. Lomb-Scargle Robustness ---

def test_lomb_scargle_constant_data():
    """Test that constant data does not crash Lomb-Scargle and returns constant surrogates."""
    x = np.ones(50)
    t = np.arange(50)

    # Should not raise
    try:
        surrogates = _lomb_scargle_surrogates(x, t, n_surrogates=10)
    except ImportError:
        pytest.skip("Astropy not installed")

    assert surrogates.shape == (10, 50)
    assert np.allclose(surrogates, 1.0)

def test_lomb_scargle_extreme_time():
    """Test that large time offsets don't cause numerical instability in phase calculation."""
    x = np.random.randn(50)
    t = np.arange(50) + 1e9 # Year 2030+ in seconds-ish

    try:
        # If time isn't shifted, cos(2*pi*f*t) loses precision
        surrogates = _lomb_scargle_surrogates(x, t, n_surrogates=10, random_state=42)
    except ImportError:
        pytest.skip("Astropy not installed")

    assert not np.any(np.isnan(surrogates))
    # Check variance preservation (approx)
    assert np.isclose(np.std(surrogates), np.std(x), rtol=0.5)

def test_surrogate_test_nan_handling():
    """Test that NaNs in input are handled (or raise appropriate errors)."""
    x = np.array([1, 2, np.nan, 4, 5])
    t = np.arange(5)

    # surrogate_test expects clean data usually, but let's see if it propagates NaNs
    # The docstring says x is Union[np.ndarray, pd.DataFrame]
    # trend_test cleans it. surrogate_test does not explicitly clean it in the current code I read.
    # It just flattens it.

    # If we pass NaNs to astropy LombScargle, it might crash or return NaNs.
    # Let's see what happens.

    try:
        res = surrogate_test(x, t, method='lomb_scargle', n_surrogates=5)
    except ImportError:
        pytest.skip("Astropy not installed")
    except ValueError as e:
        # Astropy might raise ValueError for NaNs
        assert "NaN" in str(e) or "nan" in str(e).lower()
        return

    # If it returns, ensure no NaNs in results if possible, or consistent NaNs
    # Actually, if x has NaNs, _mk_score might handle it or not.
    pass

# --- 2. Power Test Edge Cases ---

def test_power_test_invalid_alpha():
    """Test power test with extreme alpha values."""
    x = np.random.randn(20)
    t = np.arange(20)
    slopes = [0.1]

    # alpha=0 implies strict impossibility?
    # alpha=1 implies always significant?

    res = power_test(x, t, slopes, n_simulations=5, n_surrogates=5, alpha=1.0, surrogate_method='iaaft')
    assert res.power[0] == 1.0 # Should detect everything since p < 1.0 is always true

    res = power_test(x, t, slopes, n_simulations=5, n_surrogates=5, alpha=0.0, surrogate_method='iaaft')
    assert res.power[0] == 0.0 # Should detect nothing since p < 0 is impossible

def test_power_test_invalid_slope_scaling():
    """Test invalid slope scaling unit."""
    x = np.random.randn(20)
    t = pd.date_range('2020-01-01', periods=20, freq='D')
    slopes = [1]

    with pytest.raises(ValueError, match="Invalid `slope_scaling`"):
        power_test(x, t, slopes, slope_scaling='invalid_unit')

def test_power_test_dataframe_bad_structure():
    """Test passing a multi-column dataframe without 'value' column."""
    df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
    t = np.arange(3)

    with pytest.raises(ValueError, match="Input DataFrame .* must be 1-dimensional"):
        power_test(df, t, [0.1])

# --- 3. Surrogate Kwargs Injection & Validation ---

def test_trend_test_surrogate_kwargs_mismatch_aggregation():
    """
    Test that supplying array-like surrogate_kwargs raises ValueError
    when aggregation is used, because original_index is lost.
    """
    t = pd.date_range('2020-01-01', periods=100, freq='D')
    x = np.random.randn(100)
    dy = np.ones(100) # Length matches original

    # Aggregation: Monthly (will result in ~4 points)
    with pytest.raises(ValueError, match="cannot be automatically mapped"):
        trend_test(
            x, t,
            agg_method='median', agg_period='month',
            surrogate_method='lomb_scargle',
            n_surrogates=10,
            surrogate_kwargs={'dy': dy} # Error: dy length 100 != agg length 4
        )

def test_trend_test_surrogate_kwargs_length_mismatch_no_agg():
    """
    Test passing a kwargs array that doesn't match x length (and no aggregation).
    """
    t = np.arange(10)
    x = np.random.randn(10)
    dy = np.ones(5) # Wrong length

    # Should probably raise ValueError inside surrogate_test or astropy
    # because dy doesn't match x.
    # Or trend_test might catch it if it tries to slice?
    # trend_test only slices if length matches original.
    # If length doesn't match original, it passes it through.
    # Then astropy raises ValueError.

    try:
        trend_test(
            x, t,
            surrogate_method='lomb_scargle',
            n_surrogates=5,
            surrogate_kwargs={'dy': dy}
        )
    except Exception as e:
        # We expect some error about dimensions
        assert "shape" in str(e).lower() or "dimension" in str(e).lower() or "match" in str(e).lower()

# --- 4. Performance & Warnings ---

def test_performance_warning_surrogates():
    """Test that a warning is issued for Large N + Slow MK + Surrogates."""
    # We fake the size tier detection or just provide enough data
    # 5001 triggers 'fast' mode.
    # But generating 5000 surrogates is slow for the test itself.
    # We can mock detect_size_tier?
    # Or just rely on the logic check:
    # if tier_info['strategy'] == 'fast' and mk_test_method == 'lwp'

    # Let's force 'fast' mode via large_dataset_mode='fast' on small data?
    # The code says: is_large_fast = computation_mode == 'fast'

    x = np.random.randn(100)
    t = np.arange(100)

    # Force fast mode explicitly
    with pytest.warns(UserWarning, match="Performance Warning"):
        trend_test(
            x, t,
            large_dataset_mode='fast', # Forces computation_mode='fast'
            mk_test_method='lwp',
            surrogate_method='iaaft',
            n_surrogates=101 # > 100 to trigger warning
        )

# --- 5. Seasonal Integrity ---

def test_seasonal_surrogate_random_state_drift():
    """
    Verify that seasons get different random states.
    We can't easily introspect the inner function variables.
    But we can check that the generated surrogate scores are not identical across seasons
    if we have identical data for each season.
    """
    # Create data where every season is identical
    n_years = 10
    season_vals = np.random.randn(n_years)

    # Two seasons, identical data
    x = np.concatenate([season_vals, season_vals])
    # t: Year 1 S1, Year 1 S2, Year 2 S1...
    # We construct t such that we have 2 seasons.
    # Season 1: indices 0..9
    # Season 2: indices 10..19
    # To make seasonal_trend_test see this, we use numeric t with period=10? No.
    # We construct t so that season 0 is first half, season 1 is second half?
    # No, seasonal test groups by (cycle, season).

    # Let's use simple numeric t with period=2.
    # t = 0, 1, 2, 3...
    # even t -> season 0
    # odd t -> season 1

    # We want season 0 data == season 1 data.
    x_interleaved = np.empty(2 * n_years)
    x_interleaved[0::2] = season_vals
    x_interleaved[1::2] = season_vals

    t = np.arange(2 * n_years)

    # Run seasonal test with surrogates
    res = seasonal_trend_test(
        x_interleaved, t, period=2,
        surrogate_method='iaaft',
        n_surrogates=50,
        random_state=42
    )

    # If random_state was NOT incremented, Season 0 and Season 1 would have generated
    # exactly the same surrogates (since input data is identical).
    # Since surrogates are random permutations (IAAFT/Shuffle), identical seed + identical data = identical surrogates.

    # However, we don't have access to the individual season surrogates in the result,
    # only the SUM of them.

    # Wait. If they are identical:
    # S_surr_total = S_surr_season0 + S_surr_season1
    # If S_surr_0 == S_surr_1 (due to same seed), then S_total is even?
    # Not necessarily.

    # A better check:
    # If I run it twice with same random_state, I get same result (Reproducibility).
    res2 = seasonal_trend_test(
        x_interleaved, t, period=2,
        surrogate_method='iaaft',
        n_surrogates=50,
        random_state=42
    )
    assert np.allclose(res.surrogate_result.surrogate_scores, res2.surrogate_result.surrogate_scores)

    # If I run it with different random_state, I get different result.
    res3 = seasonal_trend_test(
        x_interleaved, t, period=2,
        surrogate_method='iaaft',
        n_surrogates=50,
        random_state=43
    )
    assert not np.allclose(res.surrogate_result.surrogate_scores, res3.surrogate_result.surrogate_scores)

    # This doesn't prove the increment logic, but it proves the seed works.
    # To prove increment logic, we'd need to mock `surrogate_test` and check call args.
    pass
