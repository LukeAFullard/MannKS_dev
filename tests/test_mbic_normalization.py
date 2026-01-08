
import pytest
import numpy as np
import pandas as pd
from MannKS.segmented_trend_test import segmented_trend_test, find_best_segmentation

def test_time_normalization():
    """
    Test that normalize_time=True works correctly with large timestamps (Unix epoch style).
    """
    np.random.seed(42)
    n = 100
    # Unix timestamp start (e.g., 2020-01-01)
    base_time = 1577836800.0
    # Steps of 1000 seconds
    t = base_time + np.arange(n) * 1000.0

    # Create a break at index 50
    y = np.zeros(n)
    y[:50] = 0.001 * (t[:50] - base_time) # slope 0.001 per sec relative to start
    y[50:] = 0.005 * (t[50:] - t[50]) + y[49] # slope 0.005

    # Add noise
    y += np.random.normal(0, 5, n)

    # Without normalization, slopes are tiny if relative to 0?
    # Actually Sen's slope handles large T by differencing, so slope is ~0.001.
    # But optimization might struggle with large T values for breakpoints if grid search uses them directly in ill-conditioned ways?
    # Or floating point precision (adding small step to large T).

    # Run WITH normalization
    res_norm = segmented_trend_test(y, t, n_breakpoints=1, n_bootstrap=0, normalize_time=True)

    # Check breakpoint is found near index 50 (time ~ base + 50000)
    expected_bp = base_time + 50 * 1000.0
    assert len(res_norm.breakpoints) == 1
    found_bp = res_norm.breakpoints[0]

    # Allow some margin (e.g. +/- 5 indices = 5000s)
    assert abs(found_bp - expected_bp) < 5000.0

    # Check that breakpoints are returned in ORIGINAL scale (large numbers)
    assert found_bp > base_time

def test_mbic_boundary_penalty():
    """
    Test that mBIC penalizes breakpoints near the edge more than BIC.
    """
    np.random.seed(42)
    n = 50
    t = np.arange(n)

    # Data with NO break (linear)
    y = t + np.random.normal(0, 1, n)

    # 1. Fit N=1 (Break near edge, e.g. index 5)
    # We force the optimizer to look? No, we just run find_best.
    # We want to see if mBIC rejects a "lucky" edge break that BIC might accept (or accept less reluctantly).

    # Let's manually calculate scores for a specific breakpoint to verify penalty logic.
    # But we can't easily force the function to return specific bp score.
    # We will trust find_best.

    # Let's create data with a break at index 4 (10% boundary is index 5 for n=50).
    # Break at index 3 (<10%).
    y_edge = y.copy()
    y_edge[:3] = y_edge[:3] + 10 # Jump at start

    # Fit with BIC
    res_bic = segmented_trend_test(y_edge, t, n_breakpoints=1, criterion='bic')

    # Fit with mBIC
    res_mbic = segmented_trend_test(y_edge, t, n_breakpoints=1, criterion='mbic')

    # The SAR should be identical (same optimization)
    assert np.isclose(res_bic.sar, res_mbic.sar)

    # But the mBIC score should be HIGHER than BIC score + 3*k*log(n) vs k*log(n)?
    # Wait, base mBIC is n*log(SAR/n) + 3*k*log(n).
    # BIC is n*log(SAR/n) + k*log(n). (Where k is params).
    # Here k for continuous = 2*1 + 2 = 4.
    # 3*nb*log(n) = 3*1*log(50).
    # k*log(n) = 4*log(50).
    # 3*log(50) vs 4*log(50)?
    # Actually, mBIC formula in code: 3 * n_breakpoints * log(n).
    # "Modified Schwarz Criterion" often replaces the `p*log(n)` term with something involving breakpoints.
    # The user formula: base_bic = ... + 3 * n_breakpoints * log(n_obs).
    # Regular BIC uses k * log(n). k ~ 4.
    # So 3*1 vs 4. mBIC penalty for 1 breakpoint (base) is actually lower than BIC (3 vs 4)?
    # But it ADDS boundary penalty.

    # Check if boundary penalty is applied.
    # If breakpoint is at index ~3 (t=3), range is 0-49. 10% is 4.9.
    # So 3 is < 4.9. Boundary penalty applies.
    # Penalty = log(n).

    # So mBIC = Base + log(n) = n*log(SAR/n) + 3*log(n) + log(n) = ... + 4*log(n).
    # BIC = n*log(SAR/n) + 4*log(n).
    # They might be equal in this specific parameter count case!
    # (Since k=4 for continuous n=1).

    # What if n=2?
    # BIC k = 2*2 + 2 = 6. Penalty 6*log(n).
    # mBIC penalty = 3*2*log(n) = 6*log(n).
    # Plus boundary penalties.

    # So mBIC acts like BIC but adds specific boundary penalties.
    # Let's verify the score values.

    # Check Res BIC
    n_obs = 50
    k = 4
    expected_bic = n_obs * np.log(res_bic.sar / n_obs) + k * np.log(n_obs)
    assert np.isclose(res_bic.bic, expected_bic)

    # Check Res mBIC
    # We expect boundary penalty.
    expected_mbic_base = n_obs * np.log(res_mbic.sar / n_obs) + 3 * 1 * np.log(n_obs)
    # Check if we got boundary penalty
    # If bp < 4.9 or bp > 44.1
    bp = res_mbic.breakpoints[0]
    t_min, t_max = 0, 49
    threshold = 0.1 * 49
    is_boundary = (bp - t_min < threshold) or (t_max - bp < threshold)

    if is_boundary:
        expected_mbic = expected_mbic_base + np.log(n_obs)
    else:
        expected_mbic = expected_mbic_base

    assert np.isclose(res_mbic.mbic, expected_mbic)

    # Ensure mBIC is selected as the score
    assert res_mbic.score == res_mbic.mbic

def test_find_best_mbic():
    """
    Test finding best model with mBIC.
    """
    np.random.seed(42)
    n = 40
    t = np.arange(n)
    y = t # Linear

    # With linear data, N=0 should be best.
    # N=1 might fit noise better but mBIC penalty (especially if boundary) should suppress it.

    res, _ = find_best_segmentation(y, t, max_breakpoints=2, criterion='mbic', normalize_time=True)

    assert res.n_breakpoints == 0
