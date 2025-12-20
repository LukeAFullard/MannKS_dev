import pytest
import numpy as np
import pandas as pd
from MannKenSen import trend_test

def test_slope_scaling_datetime():
    """
    Tests that the slope is correctly scaled for different time units
    when using a datetime time vector.
    """
    x = np.array([1, 2, 3, 4, 5])
    t = pd.to_datetime(['2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01'])

    # Test scaling to 'year'
    result_year = trend_test(x, t, x_unit='m', slope_scaling='year')
    assert result_year.slope_units == 'm per year'
    assert np.isclose(result_year.slope, 1.0, atol=0.01) # Should be approx 1.0 m/year
    assert np.isclose(result_year.slope_per_second, result_year.slope / (365.25 * 24 * 60 * 60), atol=1e-9)

    # Test scaling to 'day'
    result_day = trend_test(x, t, x_unit='cm', slope_scaling='day')
    assert result_day.slope_units == 'cm per day'
    assert np.isclose(result_day.slope, 1.0 / 365.25, atol=0.001) # Should be approx 1/365.25 cm/day
    assert np.isclose(result_day.slope_per_second, result_day.slope / (24 * 60 * 60), atol=1e-9)

def test_slope_scaling_numeric_warning():
    """
    Tests that a UserWarning is issued when trying to scale a slope
    with a numeric time vector.
    """
    x = np.array([1, 2, 3, 4, 5])
    t = np.array([2000, 2001, 2002, 2003, 2004])

    with pytest.warns(UserWarning, match="Cannot apply `slope_scaling`"):
        result = trend_test(x, t, x_unit='m', slope_scaling='year')

    # The slope should be unscaled, and the units should reflect this
    assert result.slope == 1.0
    assert result.slope_units == 'm per unit of t'
    # For numeric time, slope_per_second is the same as the raw slope
    assert result.slope_per_second == 1.0

def test_invalid_scaling_unit():
    """
    Tests that an invalid scaling unit raises a warning and falls back gracefully.
    """
    x = np.array([1, 2, 3, 4, 5])
    t = pd.to_datetime(['2000-01-01', '2001-01-01', '2002-01-01', '2003-01-01', '2004-01-01'])

    with pytest.warns(UserWarning, match="Slope scaling failed"):
        result = trend_test(x, t, x_unit='m', slope_scaling='invalid_unit')

    # Should fall back to units/sec
    assert result.slope_units == 'm per second'
    assert not np.isnan(result.slope)
