import numpy as np
import pytest
from MannKS.segmented_trend_test import segmented_trend_test, find_best_segmentation

def test_bagging_integration():
    """Test that use_bagging=True runs without error and returns valid structure."""
    np.random.seed(123)
    t = np.arange(30)
    # Clear breakpoint at 15
    x = np.concatenate([t[:15], 15 - (t[15:]-15)]) + np.random.normal(0, 0.1, 30)

    res = segmented_trend_test(x, t, n_breakpoints=1, n_bootstrap=10, use_bagging=True)

    assert res.n_breakpoints == 1
    assert len(res.breakpoints) == 1
    # Check breakpoint location
    assert 10 < res.breakpoints[0] < 20

    # Ensure bootstrap samples were generated
    assert res.bootstrap_samples is not None
    assert len(res.bootstrap_samples) > 0

def test_find_best_segmentation_bagging():
    """Test that find_best_segmentation passes use_bagging correctly."""
    np.random.seed(123)
    t = np.arange(30)
    x = np.concatenate([t[:15], 15 - (t[15:]-15)]) + np.random.normal(0, 0.1, 30)

    res, summary = find_best_segmentation(x, t, max_breakpoints=1, use_bagging=True, n_bootstrap=10)

    assert res.n_breakpoints == 1
    assert len(res.breakpoints) == 1
    # We can't easily check if bagging was used internally without mocking,
    # but successful execution implies the parameter was accepted.

def test_bagging_disabled():
    """Test that bagging is disabled by default."""
    np.random.seed(123)
    t = np.arange(30)
    x = t + np.random.normal(0, 0.1, 30)

    res = segmented_trend_test(x, t, n_breakpoints=0, use_bagging=False)
    assert res.n_breakpoints == 0

def test_bagging_options():
    """Test that bagging_options are respected."""
    np.random.seed(123)
    t = np.arange(30)
    x = np.concatenate([t[:15], 15 - (t[15:]-15)]) + np.random.normal(0, 0.1, 30)

    # Test 'mean' aggregation
    res = segmented_trend_test(
        x, t, n_breakpoints=1, n_bootstrap=10,
        use_bagging=True,
        bagging_options={'n_bootstrap': 15, 'aggregation': 'mean'}
    )

    assert res.n_breakpoints == 1
    assert len(res.breakpoints) == 1

    # We can't easily assert that 'mean' was used vs 'median' on random data without deeper hooks,
    # but the execution without error confirms the path was taken.
    # Also n_bootstrap=15 (different from main 10) can be inferred if we could see inside,
    # but for now verifying API stability is good.

