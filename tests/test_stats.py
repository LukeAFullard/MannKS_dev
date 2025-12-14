import pytest
import numpy as np
from MannKenSen._stats import _confidence_intervals

def test_confidence_intervals_lwp_method():
    """
    Test the LWP confidence interval method.
    """
    slopes = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    var_s = 12
    alpha = 0.05

    # With the direct method, the indices will be rounded
    lower_ci_direct, upper_ci_direct = _confidence_intervals(slopes, var_s, alpha, method='direct')

    # With the LWP method, the indices will be interpolated
    lower_ci_lwp, upper_ci_lwp = _confidence_intervals(slopes, var_s, alpha, method='lwp')

    # The results should be different
    assert lower_ci_direct != lower_ci_lwp
    assert upper_ci_direct != upper_ci_lwp

    # And the LWP results should be the result of interpolation
    assert lower_ci_lwp == pytest.approx(1.61, abs=0.01)
    assert upper_ci_lwp == pytest.approx(8.39, abs=0.01)
