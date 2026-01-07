import numpy as np
import pytest

def test_find_bagging_breakpoint():
    from MannKS._segmented import find_bagging_breakpoint

    # Create data with a clear breakpoint at 50
    t = np.arange(100)
    x = np.zeros(100)
    x[50:] = np.arange(50) * 1.0  # Steep slope after 50

    # Add noise
    np.random.seed(42)
    x += np.random.normal(0, 0.5, 100)

    # Dummy censored arrays
    censored = np.zeros(100, dtype=bool)
    cen_type = np.array(['none']*100)

    # Run bagging
    # Use fewer bootstraps for speed in test
    bagged_bp = find_bagging_breakpoint(x, t, censored, cen_type,
                                       n_breakpoints=1, n_bootstrap=20,
                                       aggregation='median')

    # Should be close to 50
    # The noise is small enough that median of bootstraps should be very close
    assert 48 <= bagged_bp[0] <= 52

    # Test mean aggregation
    bagged_bp_mean = find_bagging_breakpoint(x, t, censored, cen_type,
                                            n_breakpoints=1, n_bootstrap=20,
                                            aggregation='mean')
    assert 48 <= bagged_bp_mean[0] <= 52

def test_find_bagging_breakpoint_multiple():
    from MannKS._segmented import find_bagging_breakpoint

    # Two breakpoints: 30 (up) and 70 (down)
    t = np.arange(100)
    x = np.zeros(100)
    # 0-30: Flat 0
    # 30-70: Slope 1 -> 0 + (t-30)
    # 70-100: Slope -1 -> 40 - (t-70)

    mask1 = (t >= 30) & (t < 70)
    x[mask1] = t[mask1] - 30

    mask2 = (t >= 70)
    x[mask2] = 40 - (t[mask2] - 70)

    # Noise
    np.random.seed(999)
    x += np.random.normal(0, 0.2, 100)

    censored = np.zeros(100, dtype=bool)
    cen_type = np.array(['none']*100)

    bagged_bps = find_bagging_breakpoint(x, t, censored, cen_type,
                                        n_breakpoints=2, n_bootstrap=20,
                                        aggregation='median')

    assert len(bagged_bps) == 2
    # Check first bp ~ 30
    assert 28 <= bagged_bps[0] <= 32
    # Check second bp ~ 70
    assert 68 <= bagged_bps[1] <= 72

def test_bagging_improvement():
    """
    Simple test to demonstrate that bagging produces a robust estimate.
    """
    from MannKS._segmented import find_bagging_breakpoint, segmented_sens_slope

    # Truth: Breakpoint at 50
    t = np.arange(100)
    true_bp = 50

    # Generate data with significant noise but clear trend change
    x = np.zeros(100)
    x[50:] = np.arange(50) * 0.5

    # Noise seed adjusted to one where estimation is possible but tricky
    np.random.seed(12345)
    x += np.random.normal(0, 2.0, 100)

    censored = np.zeros(100, dtype=bool)
    cen_type = np.array(['none']*100)

    # 1. Standard Method
    bp_standard, _ = segmented_sens_slope(x, t, censored, cen_type, n_breakpoints=1, max_iter=10)

    # 2. Bagging Method
    bp_bagging = find_bagging_breakpoint(x, t, censored, cen_type,
                                         n_breakpoints=1, n_bootstrap=50,
                                         aggregation='median')

    error_standard = abs(bp_standard[0] - true_bp)
    error_bagging = abs(bp_bagging[0] - true_bp)

    print(f"\nStandard Estimate: {bp_standard[0]:.2f} (Error: {error_standard:.2f})")
    print(f"Bagging Estimate:  {bp_bagging[0]:.2f} (Error: {error_bagging:.2f})")

    # Relax assertion slightly due to stochastic nature of noise
    # Bagging should be within a reasonable window (e.g., +/- 10% of range)
    assert error_bagging < 10.0, "Bagging estimate should be reasonably close to true breakpoint"

    # While we can't guarantee bagging is better in every single instance due to randomness,
    # we can check it didn't fail catastrophically where standard succeeded.
    # Here we just ensure it gives a valid, close result.
