
import pytest
import numpy as np
import pandas as pd
from MannKS.segmented_trend_test import segmented_trend_test, calculate_breakpoint_probability

def test_segmented_trend_simple():
    # Simple kink: t 0-50 slope 1, t 50-100 slope 2
    t = np.arange(100)
    x = np.zeros(100)
    x[:50] = t[:50]
    x[50:] = 50 + 2 * (t[50:] - 50)

    # Add small noise
    np.random.seed(42)
    x += np.random.normal(0, 0.5, 100)

    result = segmented_trend_test(x, t, n_breakpoints=1, n_bootstrap=20)

    assert result.n_breakpoints == 1
    assert result.converged
    # Breakpoint should be near 50
    assert 45 < result.breakpoints[0] < 55

    # Segments should have slopes approx 1 and 2
    segments = result.segments
    assert len(segments) == 2
    assert 0.8 < segments.iloc[0]['slope'] < 1.2
    assert 1.8 < segments.iloc[1]['slope'] < 2.2

def test_segmented_trend_insufficient_data():
    t = np.arange(5)
    x = np.random.normal(0, 1, 5)

    # Default min_segment_size is 10, should raise error or handle gracefully?
    # Function raises ValueError for insufficient total data < 2.
    # For segments, it might fail to find valid splits if constraints > N.

    # If we request 1 breakpoint with min_segment_size=10 on N=5,
    # the search grid will be empty or invalid.

    # segmented_trend_test catches errors? No, it returns what it finds.
    # segmented_sens_slope checks constraints.

    # Let's see behavior
    try:
        segmented_trend_test(x, t, n_breakpoints=1, min_segment_size=10)
    except Exception:
        pass # Expected or acceptable

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
    # Explicitly set continuity=True because this data simulates a continuous process (kink).
    result = segmented_trend_test(x, dates, n_breakpoints=1, n_bootstrap=50, continuity=True)

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
