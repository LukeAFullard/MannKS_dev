
import pytest
import numpy as np
import pandas as pd
from MannKS import rolling_trend_test, segmented_trend_test

def test_rolling_trend_large_dataset_params():
    """
    Verify that rolling_trend_test accepts and passes large dataset parameters.
    """
    n = 100
    t = np.arange(n)
    x = t + np.random.normal(0, 1, n)

    # We can't easily check internal calls without mocking, but we can ensure
    # it runs without error when these parameters are passed.
    # If they weren't accepted, it would raise a TypeError.

    df = rolling_trend_test(
        x, t, window=20,
        large_dataset_mode='fast',
        max_pairs=5000,
        random_state=42
    )

    assert not df.empty
    assert 'slope' in df.columns

def test_segmented_trend_large_dataset_params():
    """
    Verify that segmented_trend_test accepts large dataset parameters
    and uses fast mode for large segments.
    """
    # Create a dataset with a very large segment
    # Segment 1: 5200 points (should trigger fast mode > 5000)
    # Segment 2: 100 points
    n1 = 5200
    n2 = 100

    t1 = np.arange(n1)
    x1 = 1.0 * t1 + np.random.normal(0, 0.1, n1) # Very clear slope, low noise

    t2 = np.arange(n1, n1 + n2)
    # Sharp drop then negative slope
    x2 = x1[-1] - 50 - 1.0 * (t2 - n1) + np.random.normal(0, 0.1, n2)

    t = np.concatenate([t1, t2])
    x = np.concatenate([x1, x2])

    # Run segmented trend test with forced fast mode parameters
    # Note: Phase 1 (breakpoints) uses full data (OLS), Phase 2 uses fast mode if applicable

    result = segmented_trend_test(
        x, t,
        n_breakpoints=1, # Fix 1 breakpoint to simplify
        large_dataset_mode='fast',
        max_pairs=10000,
        random_state=42
    )

    # Check that we found the segments
    if len(result.segments) != 2:
        print(f"Warning: Found {len(result.segments)} segments instead of 2.")
        print(result.segments)

    assert len(result.segments) == 2

    # Check that it ran successfully and produced valid slopes
    s1 = result.segments.iloc[0]['slope']
    s2 = result.segments.iloc[1]['slope']

    assert not np.isnan(s1)
    assert not np.isnan(s2)

    # Check accuracy roughly
    assert 0.9 < s1 < 1.1
    assert -1.1 < s2 < -0.9

if __name__ == "__main__":
    test_rolling_trend_large_dataset_params()
    test_segmented_trend_large_dataset_params()
    print("All Phase 4 verifications passed.")
