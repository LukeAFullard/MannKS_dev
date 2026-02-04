
import pytest
import numpy as np
from MannKS.trend_test import trend_test

def test_block_bootstrap_unsorted_input():
    """
    Verify that block bootstrap correctly handles unsorted (shuffled) input data.

    If the data is sorted internally, the variance of the S statistic (var_s)
    should be similar for both sorted and shuffled versions of the same
    autocorrelated dataset.

    If not sorted internally, shuffled data destroys serial correlation structure,
    leading to significantly different variance estimates.
    """
    # 1. Generate autocorrelated data (Red Noise)
    rng = np.random.default_rng(42)
    n = 100
    r = 0.8
    x = np.zeros(n)
    w = rng.standard_normal(n)
    for i in range(1, n):
        x[i] = r * x[i-1] + w[i]

    t = np.arange(n)

    # 2. Shuffle data (preserving x-t pairs)
    idx = rng.permutation(n)
    x_shuffled = x[idx]
    t_shuffled = t[idx]

    # 3. Run Block Bootstrap on Sorted Data (Baseline)
    res_sorted = trend_test(
        x, t,
        autocorr_method='block_bootstrap',
        n_bootstrap=500,
        random_state=42
    )

    # 4. Run Block Bootstrap on Shuffled Data
    res_shuffled = trend_test(
        x_shuffled, t_shuffled,
        autocorr_method='block_bootstrap',
        n_bootstrap=500,
        random_state=42
    )

    # 5. Assertions
    # S statistics should be identical (MK invariant to order if pairs preserved)
    assert res_sorted.s == res_shuffled.s

    # Variance estimates should be similar (within 20% tolerance)
    # Without the fix, shuffled variance was ~1/5th of sorted variance.
    # With the fix, they should be close.
    rel_diff = abs(res_sorted.var_s - res_shuffled.var_s) / res_sorted.var_s
    assert rel_diff < 0.2, f"Variance mismatch: Sorted={res_sorted.var_s}, Shuffled={res_shuffled.var_s}"

    # Ensure p-values are reasonably close
    assert abs(res_sorted.p - res_shuffled.p) < 0.1
