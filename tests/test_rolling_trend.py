import numpy as np
import pandas as pd
import pytest
from MannKS import rolling_trend_test, compare_periods, plot_rolling_trend

def test_rolling_trend_basic_numeric():
    """Test basic rolling trend calculation with numeric time."""
    n = 100
    t = np.arange(n)
    # Slope of 2, noise 1
    x = 2 * t + np.random.normal(0, 1, n)

    # Window of 20, step 5
    results = rolling_trend_test(x, t, window=20, step=5, min_size=10)

    # Should have multiple windows
    # Range 0-100. Window 20.
    # Windows: [0, 20), [5, 25), ... [80, 100)
    assert len(results) > 5

    # All slopes should be positive and roughly 2
    assert (results['slope'] > 1.5).all()
    assert (results['slope'] < 2.5).all()

    # Check required columns
    required_cols = ['window_start', 'window_end', 'slope', 'p_value', 'classification', 'C']
    assert all(col in results.columns for col in required_cols)

def test_rolling_trend_basic_datetime():
    """Test rolling trend with datetime index."""
    n = 100
    t = pd.date_range('2000-01-01', periods=n, freq='ME') # Monthly end
    x = np.arange(n) + np.random.normal(0, 1, n)

    results = rolling_trend_test(x, t, window='5YE', step='1YE', min_size=10, slope_scaling='year')

    assert len(results) > 0
    # Slope scaling: x increases by 1 per month (approx 12 per year)
    # Check if slopes are roughly 12
    # Note: slope_scaling='year' scales the per-second slope to per-year.
    # The true slope is ~1 unit/month.
    # 1 unit/month * 12 months/year = 12.
    assert np.nanmedian(results['slope']) > 10

def test_rolling_trend_min_size():
    """Test min_size filtering."""
    n = 20
    t = np.arange(n)
    x = t

    # Window size 5, min size 6 -> should return empty
    results = rolling_trend_test(x, t, window=5, step=1, min_size=6)
    assert len(results) == 0

    # Min size 5 -> should return results
    results = rolling_trend_test(x, t, window=5, step=1, min_size=5)
    assert len(results) > 0

def test_compare_periods():
    """Test before/after comparison."""
    n = 100
    t = np.arange(n)

    # Slope 1 before 50, Slope -1 after 50
    x = np.concatenate([
        1 * t[:50],
        1 * 50 - 1 * (t[50:] - 50)
    ]) + np.random.normal(0, 0.1, n)

    breakpoint = 50
    comparison = compare_periods(x, t, breakpoint)

    assert 'before' in comparison
    assert 'after' in comparison

    # Before slope should be positive (~1)
    assert comparison['before'].slope > 0.8

    # After slope should be negative (~-1)
    assert comparison['after'].slope < -0.8

    # Slope difference (after - before) ~ -2
    assert comparison['slope_difference'] < -1.5

    # Should be significant change
    assert comparison['significant_change']

def test_plot_rolling_trend_execution():
    """Test that plotting function runs without error."""
    n = 50
    t = pd.date_range('2000-01-01', periods=n, freq='ME')
    x = np.arange(n) + np.random.normal(0, 1, n)

    results = rolling_trend_test(x, t, window='2YE', step='1YE', min_size=10)

    # Should run without raising exception
    try:
        plot_rolling_trend(results, data=pd.DataFrame({'t': t, 'v': x}), time_col='t', value_col='v')
    except Exception as e:
        pytest.fail(f"Plotting raised exception: {e}")

def test_rolling_with_dataframe_input():
    """Test passing DataFrame as x input."""
    df = pd.DataFrame({
        'val': np.arange(100),
        'time': pd.date_range('2000-01-01', periods=100, freq='D')
    })

    results = rolling_trend_test(df['val'], df['time'], window='30D', step='10D')
    assert len(results) > 0
    assert 'slope' in results.columns

def test_rolling_trend_seasonal():
    """Test rolling trend with seasonal=True."""
    # Generate 10 years of monthly data
    n_years = 10
    n = n_years * 12
    t = pd.date_range('2000-01-01', periods=n, freq='ME')

    # Create seasonal pattern: month 1 is low, month 7 is high
    # Overall increasing trend
    trend = 0.5 * np.arange(n) # increasing
    seasonal_component = 10 * np.sin(2 * np.pi * np.arange(n) / 12)
    noise = np.random.normal(0, 1, n)
    x = trend + seasonal_component + noise

    # Run rolling seasonal test
    # Window 5 years, step 1 year
    results = rolling_trend_test(
        x, t,
        window='5YE',
        step='1YE',
        seasonal=True,
        period=12,
        season_type='month',
        min_size=24 # Need at least 2 years for valid seasonal test
    )

    assert len(results) > 0
    # Check that it ran seasonal logic (we can't explicitly check internal calls easily,
    # but we can check if results are reasonable).
    # Since we have a strong positive trend, slopes should be positive.
    # The seasonal component should be removed by the seasonal test logic.
    assert (results['slope'] > 0).all()
    assert 'slope' in results.columns

    # Check that scaling works (defaults to seconds if not set, but we didn't set it)
    # The slope is small (per second) if not scaled.
    # 0.5 per month -> approx 6 per year -> approx 2e-7 per second.
    # Let's check slope_per_second is small positive
    assert (results['slope_per_second'] > 0).all()
    assert (results['slope_per_second'] < 1e-5).all()
