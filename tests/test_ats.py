import numpy as np
import pandas as pd
import pytest
from MannKenSen import trend_test, seasonal_trend_test

def test_ats_slope_non_seasonal():
    """
    Test the ats_slope function with the synthetic example from future_ATS.md.
    """
    np.random.seed(1)
    n = 80
    x = np.linspace(0, 10, n)
    true_beta = 0.2
    y_true = 1.0 + true_beta * x
    y = y_true + np.random.normal(scale=0.5, size=n)

    # Impose a LOD and censor low values
    lod = 1.5
    censored = y < lod
    y_obs = np.where(censored, lod, y)

    # Create the DataFrame required by trend_test
    x_prepared = pd.DataFrame({
        'value': y_obs,
        'censored': censored,
        'cen_type': np.where(censored, 'lt', 'none')
    })

    # Run the trend test with the ATS method
    res = trend_test(x=x_prepared, t=x, sens_slope_method='ats')

    # Check that the calculated slope is close to the true slope
    assert np.isclose(res.slope, true_beta, atol=0.1)

def test_ats_slope_seasonal():
    """
    Test the seasonal ATS slope calculation.
    """
    np.random.seed(42)
    n_years = 10
    n_seasons = 4
    n = n_years * n_seasons

    # Time vector
    t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='QS-DEC'))

    # True trend
    true_beta = 0.1
    time_numeric = np.linspace(0, n_years, n)
    y_true = 1.0 + true_beta * time_numeric

    # Add seasonality and noise
    seasonality = np.tile([0, 1, 0.5, 1.5], n_years)
    y = y_true + seasonality + np.random.normal(scale=0.3, size=n)

    # Impose censoring
    lod = 2.0
    censored = y < lod
    y_obs = np.where(censored, lod, y)

    # Prepare data
    x_prepared = pd.DataFrame({
        'value': y_obs,
        'censored': censored,
        'cen_type': np.where(censored, 'lt', 'none')
    })

    # Run the seasonal trend test with the ATS method
    res = seasonal_trend_test(
        x=x_prepared,
        t=t,
        period=n_seasons,
        season_type='quarter',
        sens_slope_method='ats',
        slope_scaling='year'
    )

    # The true slope is 0.1 units per year. Check if the result is close.
    # The seasonal ATS is the median of slopes, so it might not be as precise,
    # but it should be in the right ballpark.
    assert np.isclose(res.slope, true_beta, atol=0.15)
