import numpy as np
import pytest
from MannKS._scout import RobustSegmentedTrend

def test_scout_basic():
    # 1. Generate Synthetic Data
    np.random.seed(42)
    n = 100
    t = np.linspace(0, 100, n)

    # True breakpoint at t=50
    # Segment 1: y = 2*t + 10  (t < 50)
    # Segment 2: y = -1*t + 160 (t >= 50) -> at 50, y=110. 2*50+10=110. Continuous.

    true_bp = 50
    slope1 = 2
    slope2 = -1
    intercept1 = 10

    y = np.zeros_like(t)
    mask1 = t < true_bp
    y[mask1] = slope1 * t[mask1] + intercept1
    y[~mask1] = slope2 * t[~mask1] + (slope1*true_bp + intercept1 - slope2*true_bp) # Continuous

    # Add noise
    y += np.random.normal(0, 2, n)

    # Add outliers
    y[10] += 50 # Spike
    y[80] -= 50 # Spike

    # 2. Fit Model
    model = RobustSegmentedTrend(n_breakpoints=1)
    model.fit(t, y)

    # 3. Check Results
    assert len(model.breakpoints_) == 1
    assert abs(model.breakpoints_[0] - true_bp) < 5 # Should be close to 50

    # Check slopes (Robust Refiner should ignore outliers)
    s1 = model.segments_[0]['slope']
    s2 = model.segments_[1]['slope']

    # Tolerances might need adjustment depending on noise and robustness
    assert abs(s1 - 2) < 0.2
    assert abs(s2 - -1) < 0.2

    # 4. Predict
    y_pred = model.predict(t)
    assert len(y_pred) == n
    assert not np.any(np.isnan(y_pred))

def test_scout_censored_dummy():
    # Test that censored arguments are accepted and processed
    np.random.seed(42)
    t = np.arange(20)
    x = t * 1.0 # Simple linear

    censored = np.zeros(20, dtype=bool)
    censored[0] = True # One censored point
    cen_type = np.array(['not']*20, dtype=object)
    cen_type[0] = 'lt'

    model = RobustSegmentedTrend(n_breakpoints=0)
    model.fit(t, x, censored=censored, cen_type=cen_type)

    assert len(model.segments_) == 1
    assert abs(model.segments_[0]['slope'] - 1.0) < 0.1

def test_scout_no_breakpoints():
    # Test with n_breakpoints=0 (Standard Robust Regression)
    np.random.seed(42)
    t = np.linspace(0, 10, 50)
    x = 3 * t + 5 + np.random.normal(0, 0.5, 50)

    model = RobustSegmentedTrend(n_breakpoints=0)
    model.fit(t, x)

    assert len(model.breakpoints_) == 0
    assert len(model.segments_) == 1

    slope = model.segments_[0]['slope']
    intercept = model.segments_[0]['intercept']

    assert abs(slope - 3) < 0.2
    assert abs(intercept - 5) < 1.0

def test_scout_perfect_fit_flat():
    # Edge case: perfect flat line (sigma -> 0)
    t = np.linspace(0, 10, 10)
    x = np.ones(10) * 5

    model = RobustSegmentedTrend(n_breakpoints=1)
    model.fit(t, x)

    # Should not crash, slope should be 0
    s1 = model.segments_[0]['slope']
    assert s1 == 0 or np.isnan(s1) # Depending on Sen's slope behavior with identical values
    if not np.isnan(s1):
        assert abs(s1) < 1e-10
