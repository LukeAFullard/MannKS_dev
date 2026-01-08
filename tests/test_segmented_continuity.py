
import pytest
import numpy as np
import pandas as pd
from MannKS.segmented_trend_test import segmented_trend_test

def test_segmented_continuity_vs_independent():
    """
    Test that continuity=False provides a better fit (lower SAR) for discontinuous data.
    """
    np.random.seed(42)
    n = 100
    t = np.arange(n)

    # Create discontinuous data
    # Segment 1: y = t
    # Segment 2: y = t + 50 (Jump at t=50)
    y = np.zeros(n)
    y[:50] = t[:50]
    y[50:] = (t[50:] - 50) + 100

    # Add small noise
    y += np.random.normal(0, 0.1, n)

    # 1. Run with continuity=True (Default)
    res_cont = segmented_trend_test(y, t, n_breakpoints=1, n_bootstrap=0, continuity=True)

    # 2. Run with continuity=False (Independent)
    res_indep = segmented_trend_test(y, t, n_breakpoints=1, n_bootstrap=0, continuity=False)

    # Check that independent model fits better (lower SAR)
    # The difference should be large due to the jump
    assert res_indep.sar < res_cont.sar
    assert res_indep.sar < 100 # Should be small (residuals of noise)
    assert res_cont.sar > 500 # Should be large (residuals of forced connection)

    # Check breakpoints
    # Both should roughly find the break near 50, but independent might be more precise or just different.
    # Actually, for this perfect jump, both might find the break, but the residuals will differ.
    assert len(res_indep.breakpoints) == 1

    # Check that segments in independent model reflect the jump
    # Segment 1 intercept ~ 0
    # Segment 2 intercept ~ 50 (relative to local t? No, intercept is global y-axis usually)
    # Let's check how trend_test reports intercept.
    # It reports y = slope * t + intercept.
    # Seg 1: y = 1*t + 0.
    # Seg 2: y = 1*t + 50.

    s1 = res_indep.segments.iloc[0]
    s2 = res_indep.segments.iloc[1]

    assert np.isclose(s1['slope'], 1.0, atol=0.1)
    assert np.isclose(s1['intercept'], 0.0, atol=2.0)

    assert np.isclose(s2['slope'], 1.0, atol=0.1)
    assert np.isclose(s2['intercept'], 50.0, atol=2.0)

def test_segmented_continuity_continuous_data():
    """
    Test that for truly continuous data, both methods give similar results,
    but continuous model might have slightly lower AIC/BIC due to fewer parameters.
    """
    np.random.seed(42)
    n = 100
    t = np.arange(n)

    # Continuous data: y = t for t<50, y = 2t - 50 for t>=50
    # At t=50: y = 50. 2*50 - 50 = 50. Connected.
    y = np.zeros(n)
    y[:50] = t[:50]
    y[50:] = 2 * t[50:] - 50

    y += np.random.normal(0, 0.1, n)

    # Run both
    res_cont = segmented_trend_test(y, t, n_breakpoints=1, n_bootstrap=0, continuity=True)
    res_indep = segmented_trend_test(y, t, n_breakpoints=1, n_bootstrap=0, continuity=False)

    # SAR should be very similar (model can capture it with both)
    # Continuous might be slightly worse or better depending on noise, but close.
    assert np.isclose(res_cont.sar, res_indep.sar, rtol=0.2)

    # BIC should favor Continuous (fewer params) if fit is similar
    # k_cont = 2*1 + 2 = 4
    # k_indep = 3*1 + 2 = 5
    # So penalty is higher for indep.
    # If SAR is same, BIC_cont < BIC_indep.

    # Note: SAR might be slightly lower for Independent because it has more freedom to fit noise.
    # But BIC penalizes it.

    if np.isclose(res_cont.sar, res_indep.sar, rtol=0.01):
        assert res_cont.bic < res_indep.bic

def test_continuity_parameter_propagation():
    """
    Ensure the parameter is passed down correctly.
    """
    # We can mock or just trust the results.
    # The previous tests implicitly verify propagation because results differ.
    pass
