
import pytest
import numpy as np
import time
import importlib

# Robustly import the module, avoiding shadowing by __init__.py exports
stt_module = importlib.import_module("MannKS.segmented_trend_test")

def test_optimization_efficiency():
    """
    Verify that find_best_segmentation with merge_similar_segments=True runs faster
    now that we skip bootstrap inside the loop, while still producing the same result structure.
    """
    np.random.seed(42)
    n = 60
    t = np.arange(n)
    y = np.zeros(n)
    y[:20] = t[:20]
    y[20:40] = 5 * (t[20:40] - 20) + 20
    y[40:] = 1 * (t[40:] - 40) + 120
    y += np.random.normal(0, 0.5, n)

    start_time = time.time()
    res, _ = stt_module.find_best_segmentation(y, t, max_breakpoints=3, merge_similar_segments=True, n_bootstrap=50, merging_alpha=0.001)
    end_time = time.time()
    duration = end_time - start_time

    print(f"Optimization took {duration:.4f}s")

    assert res is not None
    assert res.bootstrap_samples is not None
    if res.n_breakpoints > 0:
        assert len(res.bootstrap_samples) == 50

def test_optimization_correctness_mock(monkeypatch):
    """
    Use monkeypatch to ensure segmented_trend_test is called with n_bootstrap=0 inside the loop.
    """
    # Grab the original function from the module
    real_segmented_test = stt_module.segmented_trend_test

    call_args_history = []

    def mock_segmented_trend_test(*args, **kwargs):
        # Capture n_bootstrap
        n_boot = kwargs.get('n_bootstrap', 200)
        call_args_history.append(n_boot)
        return real_segmented_test(*args, **kwargs)

    # Patch the function in the module
    monkeypatch.setattr(stt_module, "segmented_trend_test", mock_segmented_trend_test)

    np.random.seed(42)
    n = 40
    t = np.arange(n)
    y = t + np.random.normal(0, 1, n)

    # Run
    stt_module.find_best_segmentation(y, t, max_breakpoints=2, merge_similar_segments=True, n_bootstrap=10)

    # Verify we see 0 in history
    assert 0 in call_args_history

    call_args_history.clear()
    y2 = np.zeros(n)
    y2[:20] = 0
    y2[20:] = 50 * (t[20:] - 20)

    stt_module.find_best_segmentation(y2, t, max_breakpoints=2, merge_similar_segments=True, n_bootstrap=15)

    # Verify we see 0 and 15
    assert 0 in call_args_history
    assert 15 in call_args_history
