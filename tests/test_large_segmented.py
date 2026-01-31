
import numpy as np
import pandas as pd
import pytest
import time
from MannKS import segmented_trend_test

def test_large_segmented_aggregation():
    """
    Test that segmented_trend_test handles large datasets (N > 10,000) efficiently
    using the new aggregation logic for Phase 1.
    """
    N = 15000  # Threshold is 10,000
    t = pd.date_range(start='2000-01-01', periods=N, freq='h')

    # Create data with 1 breakpoint at index 7500
    x = np.zeros(N)
    x[:7500] = np.linspace(0, 10, 7500)
    x[7500:] = np.linspace(10, 0, 7500)

    # Add noise
    rng = np.random.default_rng(42)
    x += rng.normal(0, 0.5, N)

    # Run test
    start = time.time()
    res = segmented_trend_test(
        x, t,
        max_breakpoints=1,
        large_dataset_mode='auto',
        random_state=42
    )
    end = time.time()

    # Checks
    assert res.n_breakpoints == 1
    # Expected breakpoint around index 7500
    expected_bp = t[7500]
    bp = res.breakpoints[0]
    diff = abs(bp - expected_bp)
    assert diff.days < 7

    # Ensure it was fast (aggregation worked)
    assert (end - start) < 20.0 # Liberal bound, usually < 2s

def test_custom_aggregation_parameters():
    """
    Test that user can override aggregation parameters.
    Force aggregation on a smaller dataset (N=2000) by setting threshold to 1000.
    """
    N = 2000
    t = pd.date_range(start='2000-01-01', periods=N, freq='D')

    # Breakpoint at 1000
    x = np.zeros(N)
    x[:1000] = np.linspace(0, 10, 1000)
    x[1000:] = np.linspace(10, 0, 1000)
    x += np.random.normal(0, 0.1, N)

    # Run with custom threshold
    res = segmented_trend_test(
        x, t,
        max_breakpoints=1,
        large_dataset_mode='auto',
        aggregation_threshold=1000, # Force aggregation
        aggregation_target=500,     # Coarser bins
        random_state=42
    )

    assert res.n_breakpoints == 1
    bp = res.breakpoints[0]
    expected_bp = t[1000]
    assert abs(bp - expected_bp).days < 10

def test_large_segmented_bagging():
    """
    Test that bagging works on large datasets using the aggregated data.
    """
    N = 12000 # Just above threshold
    t = pd.date_range(start='2000-01-01', periods=N, freq='h')

    x = np.zeros(N)
    half = N // 2
    x[:half] = np.linspace(0, 10, half)
    x[half:] = np.linspace(10, 0, half)
    x += np.random.normal(0, 1.0, N)

    # Run with bagging
    res = segmented_trend_test(
        x, t,
        max_breakpoints=1,
        large_dataset_mode='auto',
        use_bagging=True,
        n_bootstrap=5,
        random_state=42
    )

    assert res.n_breakpoints == 1
    assert res.bootstrap_samples is not None
    assert len(res.bootstrap_samples) == 5
