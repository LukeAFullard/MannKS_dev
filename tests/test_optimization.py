import pytest
import numpy as np
import time
from MannKS._stats import _sens_estimator_unequal_spacing
from MannKS._segmented import segmented_sens_slope
from MannKS.segmented_trend_test import segmented_trend_test

def test_max_pairs_sampling():
    """Test that max_pairs reduces execution time for large N without breaking slope calculation."""
    # Create large synthetic data
    n = 2000
    t = np.linspace(0, 100, n)
    # y = 2x + noise
    x = 2 * t + np.random.normal(0, 1, n)

    # 1. Full pairs
    t0 = time.time()
    slope_full = np.median(_sens_estimator_unequal_spacing(x, t))
    dt_full = time.time() - t0

    # 2. Limited pairs (e.g., 5000 random pairs out of ~2 million)
    t0 = time.time()
    slope_sampled = np.median(_sens_estimator_unequal_spacing(x, t, max_pairs=5000))
    dt_sampled = time.time() - t0

    print(f"\nFull: {dt_full:.4f}s, Slope={slope_full:.4f}")
    print(f"Sampled: {dt_sampled:.4f}s, Slope={slope_sampled:.4f}")

    # Check Speedup
    # Sampling should be significantly faster for N=2000
    assert dt_sampled < dt_full

    # Check Accuracy
    # Slope should be close to 2.0 (within reason for random sampling)
    assert np.isclose(slope_sampled, 2.0, atol=0.1)

def test_optimizer_vs_grid_search():
    """Test that use_optimizer=True finds a similar breakpoint to the default grid search, but faster."""
    # Data with 1 breakpoint
    n = 100
    t = np.linspace(0, 100, n)
    bp_true = 60
    # y = x before 60, y = 60 + 0.5(x-60) after 60
    x = np.where(t <= bp_true, t, 60 + 0.5 * (t - bp_true))
    # Add noise
    x += np.random.normal(0, 0.5, n)

    censored = np.zeros(n, dtype=bool)
    cen_type = np.array(['not']*n)

    # 1. Default (Grid Search)
    t0 = time.time()
    bp_grid, _ = segmented_sens_slope(x, t, censored, cen_type, n_breakpoints=1, max_iter=10)
    dt_grid = time.time() - t0

    # 2. Optimizer (minimize_scalar)
    t0 = time.time()
    bp_opt, _ = segmented_sens_slope(x, t, censored, cen_type, n_breakpoints=1, max_iter=10, use_optimizer=True)
    dt_opt = time.time() - t0

    print(f"\nGrid: {dt_grid:.4f}s, BP={bp_grid[0]:.4f}")
    print(f"Opt:  {dt_opt:.4f}s, BP={bp_opt[0]:.4f}")

    # Accuracy check
    assert np.abs(bp_grid[0] - bp_true) < 5.0
    assert np.abs(bp_opt[0] - bp_true) < 5.0

    # Consistency check
    assert np.abs(bp_grid[0] - bp_opt[0]) < 2.0

def test_full_precision_polish():
    """
    Verify that segmented_trend_test calculates the final segment slopes using FULL precision
    even when max_pairs is set for the search.
    """
    # Create data with 2 segments: Slope 2.0 then Slope -2.0
    n = 500
    t = np.linspace(0, 100, n)
    x = np.where(t < 50, 2 * t, 100 - 2 * (t - 50))
    x += np.random.normal(0, 0.1, n)

    # Run with extreme max_pairs limitation for search (e.g. 10 pairs - very noisy search)
    # But final result should be accurate because it ignores max_pairs
    result = segmented_trend_test(
        x, t, n_breakpoints=1,
        max_pairs=10,  # Extreme limit for search
        use_optimizer=True
    )

    # Check that segments were found
    assert result.n_breakpoints == 1

    # The final slopes should be very close to 2.0 and -2.0
    # If max_pairs=10 was used for the final calc, the variance would be HUGE.
    s1 = result.segments.iloc[0]['slope']
    s2 = result.segments.iloc[1]['slope']

    print(f"\nSlopes with Polishing: {s1:.4f}, {s2:.4f}")

    assert np.isclose(s1, 2.0, atol=0.1)
    assert np.isclose(s2, -2.0, atol=0.1)
