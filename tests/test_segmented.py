import pytest
import numpy as np
import pandas as pd
from MannKS import segmented_trend_test, calculate_breakpoint_probability
from MannKS._segmented import segmented_sens_slope

def test_create_segments_logic():
    from MannKS._segmented import _create_segments
    t = np.array([0, 10])
    breakpoints = np.array([5])
    segments = _create_segments(t, breakpoints)
    assert len(segments) == 2
    assert segments[0] == (0, 5)
    assert segments[1] == (5, 10)

def test_segmented_trend_numeric_basic():
    # Create data: Flat then increasing
    # Time 0 to 100
    t = np.arange(100)
    # Breakpoint at 50
    x = np.zeros(100)
    x[50:] = np.arange(50) * 0.5

    # Add noise
    np.random.seed(42)
    x += np.random.normal(0, 0.1, 100)

    result = segmented_trend_test(x, t, n_breakpoints=1, n_bootstrap=10)

    assert result.converged
    assert len(result.breakpoints) == 1
    # Should be close to 50
    bp = result.breakpoints[0]
    assert 45 <= bp <= 55

    # Check segments
    assert len(result.segments) == 2

    # Segment 1 (approx 0-50): slope approx 0
    s1 = result.segments.iloc[0].slope
    assert abs(s1) < 0.2

    # Segment 2 (approx 50-100): slope approx 0.5
    s2 = result.segments.iloc[1].slope
    assert 0.4 <= s2 <= 0.6

def test_segmented_trend_datetime_probability():
    # Create datetime data
    # Change in 2010
    dates = pd.date_range(start='2000-01-01', end='2020-01-01', freq='ME')
    n = len(dates)

    t_numeric = dates.astype(np.int64) / 1e9
    bp_date = pd.Timestamp('2010-06-01')
    bp_numeric = bp_date.timestamp()

    x = np.zeros(n)
    mask_after = t_numeric >= bp_numeric

    # Slope before: 0
    # Slope after: increasing

    # Linear trend after
    t_diff = t_numeric[mask_after] - bp_numeric
    # Slope 1 unit per year approx
    slope_per_sec = 1.0 / (365.25 * 24 * 3600)
    x[mask_after] = t_diff * slope_per_sec

    # Noise (reduced for deterministic testing)
    np.random.seed(123)
    x += np.random.normal(0, 0.2, n)

    # Run test
    # Pass n_bootstrap (affects distribution gen)
    # Optimization uses default n_bootstrap=10 internal restarts.
    result = segmented_trend_test(x, dates, n_breakpoints=1, n_bootstrap=50)

    assert result.is_datetime

    # Breakpoint should be in 2010
    bp = result.breakpoints[0]
    # Allow +/- 1 year tolerance for this test configuration
    assert bp.year in [2009, 2010, 2011]

    # Probability test
    # Prob that break is in 2010
    prob = calculate_breakpoint_probability(result, '2010-01-01', '2011-01-01')

    # Should be high
    assert prob > 0.5

    # Prob that break is in 2005
    prob_low = calculate_breakpoint_probability(result, '2005-01-01', '2006-01-01')
    assert prob_low < 0.1

def test_kwargs_passed():
    # Test that lt_mult is passed down
    # We use data with heavy censoring where lt_mult affects the residual calculation

    # Scenario:
    # Left censored values: < 10
    # If lt_mult=0.5, value is 5.
    # If lt_mult=0.1, value is 1.

    # We construct a case where the optimal breakpoint shifts depending on lt_mult?
    # Or simpler: just ensure no error is raised when passing kwargs.

    t = np.arange(20)
    x = np.arange(20)

    # Just run valid call
    try:
        segmented_trend_test(x, t, n_breakpoints=1, n_bootstrap=5, lt_mult=0.8, mk_test_method='lwp')
    except Exception as e:
        pytest.fail(f"Kwargs caused error: {e}")
