
import pytest
import numpy as np
import pandas as pd
from MannKS import trend_test, seasonal_trend_test

def test_trend_test_attributes():
    """
    Verify that trend_test returns an object with scaled_lower_ci and scaled_upper_ci attributes.
    """
    t = pd.date_range('2020-01-01', periods=20, freq='D')
    x = np.linspace(0, 10, 20)

    # Test with scaling
    res = trend_test(x, t, slope_scaling='year')
    assert hasattr(res, 'scaled_lower_ci')
    assert hasattr(res, 'scaled_upper_ci')
    assert hasattr(res, 'scaled_slope')

    # Values should match lower_ci/upper_ci when scaling is active
    assert res.scaled_lower_ci == res.lower_ci
    assert res.scaled_upper_ci == res.upper_ci

    # Test without scaling
    res_raw = trend_test(x, t)
    assert hasattr(res_raw, 'scaled_lower_ci')
    assert hasattr(res_raw, 'scaled_upper_ci')
    # If no scaling, scaled_X should equal unscaled X (or whatever lower_ci is)
    assert res_raw.scaled_lower_ci == res_raw.lower_ci

def test_seasonal_trend_test_attributes():
    """
    Verify that seasonal_trend_test returns an object with scaled_lower_ci and scaled_upper_ci attributes.
    """
    t = pd.date_range('2020-01-01', periods=24, freq='ME')
    x = np.linspace(0, 10, 24)

    # Test with scaling
    res = seasonal_trend_test(x, t, slope_scaling='year')
    assert hasattr(res, 'scaled_lower_ci')
    assert hasattr(res, 'scaled_upper_ci')
    assert hasattr(res, 'scaled_slope')

    # Values should match lower_ci/upper_ci when scaling is active
    assert res.scaled_lower_ci == res.lower_ci
    assert res.scaled_upper_ci == res.upper_ci

    # Test without scaling
    res_raw = seasonal_trend_test(x, t)
    assert hasattr(res_raw, 'scaled_lower_ci')
    assert hasattr(res_raw, 'scaled_upper_ci')
    assert res_raw.scaled_lower_ci == res_raw.lower_ci
