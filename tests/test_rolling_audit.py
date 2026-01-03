import pytest
import pandas as pd
import numpy as np
from MannKS import rolling_trend_test, compare_periods

def test_rolling_default_step_offset():
    """Verify that default step for DateOffset is the window size (non-overlapping)."""
    n = 100
    t = pd.date_range('2000-01-01', periods=n, freq='ME') # Monthly
    x = np.random.randn(n)

    # Window '1YE' (Year End).
    # Default step should be '1YE' (non-overlapping).
    # Data spans ~8 years.
    # We expect roughly 8 windows.
    results = rolling_trend_test(x, t, window='1YE', min_size=5)

    assert len(results) > 0
    # Check that windows don't overlap significantly (or at all).
    # Start of second window should be start of first + 1 Year (approximately).
    w1_start = results.iloc[0]['window_start']
    w2_start = results.iloc[1]['window_start']

    # 1 Year diff
    diff = w2_start - w1_start
    # Should be approx 365 days (accept 330+ to account for offset behavior like Jan->Dec)
    assert diff.days >= 330

def test_compare_periods_insufficient_warning():
    """Test that compare_periods warns when data is insufficient."""
    t = np.arange(10)
    x = np.random.randn(10)

    # Breakpoint at 1 -> 'before' has 1 point, 'after' has 9
    with pytest.warns(UserWarning, match="Insufficient data"):
        compare_periods(x, t, breakpoint=1)

def test_rolling_offset_import_robustness():
    """
    Implicitly tests the import logic by running a test that requires offset parsing.
    """
    t = pd.date_range('2000-01-01', periods=20, freq='ME')
    x = np.random.randn(20)
    # '1YE' requires parsing
    results = rolling_trend_test(x, t, window='1YE', min_size=2)
    assert len(results) > 0
