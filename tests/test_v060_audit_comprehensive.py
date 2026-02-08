
import pytest
import numpy as np
import pandas as pd
from MannKS import trend_test, seasonal_trend_test, power_test, surrogate_test
from MannKS.seasonal_trend_test import seasonal_trend_test

# --- 1. Reproducibility Tests ---

def test_surrogate_test_reproducibility():
    """Verify that random_state ensures identical results."""
    x = np.random.randn(50)
    t = np.arange(50)

    res1 = surrogate_test(x, t, method='iaaft', n_surrogates=20, random_state=42)
    res2 = surrogate_test(x, t, method='iaaft', n_surrogates=20, random_state=42)

    assert np.allclose(res1.surrogate_scores, res2.surrogate_scores)
    assert res1.p_value == res2.p_value

    # Different state
    res3 = surrogate_test(x, t, method='iaaft', n_surrogates=20, random_state=43)
    # Extremely unlikely to be identical
    assert not np.allclose(res1.surrogate_scores, res3.surrogate_scores)

def test_power_test_reproducibility():
    """Verify power_test reproducibility."""
    x = np.random.randn(30)
    t = np.arange(30)
    slopes = [0.1]

    # Run twice
    res1 = power_test(x, t, slopes, n_simulations=10, n_surrogates=20, random_state=123)
    res2 = power_test(x, t, slopes, n_simulations=10, n_surrogates=20, random_state=123)

    assert np.allclose(res1.power, res2.power)
    if np.isnan(res1.min_detectable_trend):
        assert np.isnan(res2.min_detectable_trend)
    else:
        assert res1.min_detectable_trend == res2.min_detectable_trend

# --- 2. Data Integrity Tests ---

def test_input_immutability():
    """Test that input arrays/DataFrames are not modified in place."""
    # Dataframe case
    # FIX: Add cen_type to make it a valid "full" dataframe
    df = pd.DataFrame({
        'value': [1, 2, 3, 4, 5],
        'censored': [False]*5,
        'cen_type': ['not']*5
    })
    df_orig = df.copy()
    t = pd.date_range('2020-01-01', periods=5)

    _ = trend_test(df, t)

    pd.testing.assert_frame_equal(df, df_orig)

    # Array case
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    x_orig = x.copy()
    t_num = np.arange(5)

    _ = power_test(x, t_num, [0.1], n_simulations=5, n_surrogates=20)

    assert np.array_equal(x, x_orig)

# --- 3. Seasonal Surrogate Kwargs Slicing (The Complex Part) ---

def test_seasonal_kwargs_matching_original_no_agg():
    """
    Case A: Kwarg length == Original N. Aggregation = 'none'.
    Should slice correctly.
    """
    n = 24 # 2 years
    t = pd.date_range('2020-01-01', periods=n, freq='ME')
    x = np.random.randn(n)

    # Error array matching original
    dy = np.arange(n).astype(float)

    try:
        seasonal_trend_test(
            x, t, season_type='month',
            surrogate_method='iaaft', n_surrogates=5,
            surrogate_kwargs={'dy': dy}
        )
    except Exception as e:
        pytest.fail(f"Should have sliced dy correctly: {e}")

def test_seasonal_kwargs_matching_original_WITH_agg():
    """
    Case B: Kwarg length == Original N. Aggregation = 'median'.
    Should FAIL because mapping is ambiguous.
    """
    # FIX: Use enough data (2 years) so that after aggregation we have >1 point per season
    # 2 years daily data = ~730 points.
    # Aggregation 'median' by month -> 24 points (12 seasons x 2 cycles).
    # Season 1 (Jan) has 2 points. n=2. Code runs.

    n_days = 730
    t = pd.date_range('2020-01-01', periods=n_days, freq='D')
    x = np.random.randn(n_days)

    # dy matches original length
    dy = np.arange(n_days)

    # If we pass dy length 730, and use aggregation,
    # the code should raise ValueError because it can't map 730 dy values to the 24 aggregated values.

    with pytest.raises(ValueError, match="cannot be automatically mapped"):
        seasonal_trend_test(
            x, t, season_type='month', agg_method='median',
            surrogate_method='iaaft', n_surrogates=5,
            surrogate_kwargs={'dy': dy}
        )

def test_seasonal_kwargs_matching_aggregated():
    """
    Case C: Kwarg length == Aggregated N.
    Should work.
    """
    # Daily data for 2 months (Jan, Feb).
    t = pd.date_range('2020-01-01', periods=59, freq='D')
    x = np.random.randn(59)

    # Aggregated length will be 2 (Jan, Feb).
    # We pass dy of length 2.
    dy = np.array([0.1, 0.2])

    try:
        seasonal_trend_test(
            x, t, season_type='month', agg_method='median',
            surrogate_method='iaaft', n_surrogates=5,
            surrogate_kwargs={'dy': dy}
        )
    except Exception as e:
        pytest.fail(f"Should have accepted aggregated kwargs: {e}")

def test_seasonal_kwargs_alignment_pandas():
    """
    Case D: Kwarg is Pandas Series with Index.
    Should align by index if available?
    Code checks `original_index` column.
    """
    n = 24
    t = pd.date_range('2020-01-01', periods=n, freq='ME')
    x = pd.Series(np.random.randn(n), index=t)

    # dy as Series with same index
    dy = pd.Series(np.arange(n), index=t)

    # No aggregation
    try:
        seasonal_trend_test(
            x, t, season_type='month',
            surrogate_method='iaaft', n_surrogates=5,
            surrogate_kwargs={'dy': dy}
        )
    except Exception as e:
        pytest.fail(f"Pandas Series alignment failed: {e}")

# --- 4. Edge Cases ---

def test_n_surrogates_one():
    """Test minimal surrogate count."""
    x = np.random.randn(20)
    t = np.arange(20)
    res = surrogate_test(x, t, n_surrogates=1)
    assert len(res.surrogate_scores) == 1
    # p-value = (n_extreme + 1) / (n + 1). For n=1, p can be 1/2 or 2/2.
    assert res.p_value in [0.5, 1.0]

def test_constant_input_power_test():
    """Power test with constant input (zero variance noise)."""
    x = np.ones(20)
    t = np.arange(20)

    slopes = [0.1]
    # n_surrogates must be >= 19 to detect p < 0.05
    res = power_test(x, t, slopes, n_simulations=5, n_surrogates=20, surrogate_method='lomb_scargle')

    # With n_surrogates=20, min p-value is ~0.048 < 0.05.
    # The original signal (trend) is perfectly monotonic (max S).
    # Surrogates (phase-shuffled trend) are likely not perfectly monotonic due to spectral leakage/noise.
    # Thus S_orig > S_surr for all surrogates, leading to significance.
    assert res.power[0] == 1.0
