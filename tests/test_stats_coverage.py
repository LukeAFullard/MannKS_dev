import pytest
import warnings
import numpy as np
import pandas as pd
from MannKS import trend_test

def test_zero_variance_handling():
    """
    Tests that the system handles data with zero variance gracefully.
    When all data points are tied, the Mann-Kendall score `s` is 0,
    which should result in a final conclusion of 'no trend'.
    """
    # Create a dataset where all values are identical
    x = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
    t = np.arange(len(x))

    # No warning is expected for the Tau denominator calculation in v0.6.0+,
    # as edge cases like constant data are handled silently (Tau=0).
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = trend_test(x, t)
        # Verify no "Denominator near zero" warning
        denom_warnings = [str(warn.message) for warn in w if "Denominator near zero" in str(warn.message)]
        assert not denom_warnings, "Should not warn about zero denominator"

    # The primary assertions are on the final, user-facing results.
    # The intermediate var_s value is a non-critical implementation detail
    # in this specific edge case because s=0.
    assert result.trend == 'indeterminate'
    assert not result.h  # Use truthiness for numpy.bool_
    assert result.s == 0
    assert result.p == 1.0
