
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

    # Break at index 3 (<10%).
    y_edge = y.copy()
    y_edge[:3] = y_edge[:3] + 10 # Jump at start

    # Fit with BIC (Default continuity=False, k=5 for N=1)
    # k = 3*1 + 2 = 5 (Slopes(2) + Intercepts(2) + BP(1))
    res_bic = segmented_trend_test(y_edge, t, n_breakpoints=1, criterion='bic')

    # Fit with mBIC
    res_mbic = segmented_trend_test(y_edge, t, n_breakpoints=1, criterion='mbic')

    # The SAR should be identical (same optimization)
    assert np.isclose(res_bic.sar, res_mbic.sar)

    # Check Res BIC
    n_obs = 50
    k = 5 # Adjusted for default continuity=False
    expected_bic = n_obs * np.log(res_bic.sar / n_obs) + k * np.log(n_obs)
    assert np.isclose(res_bic.bic, expected_bic)

    # Check Res mBIC
    # Formula: n * log(SAR/n) + 3 * n_breakpoints * log(n) + boundary_penalty
    expected_mbic_base = n_obs * np.log(res_mbic.sar / n_obs) + 3 * 1 * np.log(n_obs)

    # Check if we got boundary penalty
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

    res, _ = find_best_segmentation(y, t, max_breakpoints=2, criterion='mbic', normalize_time=True)

    assert res.n_breakpoints == 0
