
import pytest
import numpy as np
import pandas as pd
from MannKS.power import power_test
from MannKS.preprocessing import prepare_censored_data

def test_power_test_slope_scaling():
    """Verify that slope_scaling works correctly."""
    t = pd.date_range('2020-01-01', periods=100, freq='D')
    x = np.random.normal(0, 1, 100)

    # Define a trend of 1 unit per year.
    # In seconds, this is ~3.17e-8 units/sec.
    # If we pass 1.0 with unit='year', it should be converted to ~3.17e-8.
    # The noise sigma is 1. Over 100 days (~0.27 yr), the trend contribution is 0.27.
    # This is small compared to noise (sigma=1). Power should be low.

    res = power_test(
        x, t, slopes=[1.0], n_simulations=10, n_surrogates=20,
        slope_scaling='year'
    )

    # If scaling FAILED and it used 1.0 unit/sec, trend would be massive -> Power 1.0.
    # If scaling WORKED, trend is small -> Power < 1.0 (likely ~0.05 - 0.2 depending on luck)

    assert res.power[0] < 0.9, f"Power too high ({res.power[0]}), scaling likely failed."
    assert res.slope_scaling == 'year'

def test_power_test_dataframe_input():
    """Verify robust handling of DataFrame input."""
    t = np.arange(20)
    df = pd.DataFrame({'value': np.random.normal(0, 1, 20), 'censored': False})

    # This previously failed because it flattened the DF. Now it should extract 'value'.
    res = power_test(df, t, slopes=[0.1], n_simulations=5, n_surrogates=20)

    assert res.n_simulations == 5

def test_power_test_dataframe_input_prepared():
    """Verify robust handling of prepare_censored_data output."""
    t = np.arange(20)
    # Even if we have censored data, power_test treats it as noise source (values only).
    df_prep = prepare_censored_data(['1', '2', '3'] * 6 + ['4', '5']) # 20 items

    # Should run without error
    res = power_test(df_prep, t, slopes=[0.1], n_simulations=5, n_surrogates=20)
    assert res.n_simulations == 5

def test_power_test_dataframe_error():
    """Verify error when DataFrame has no 'value' and multiple columns."""
    t = np.arange(20)
    df = pd.DataFrame({'a': np.arange(20), 'b': np.arange(20)})

    # Message changed due to _prepare_data usage
    with pytest.raises(ValueError, match="contain a 'value' column"):
        power_test(df, t, slopes=[0.1], n_simulations=5, n_surrogates=20)

def test_power_test_invalid_unit():
    """Verify that invalid slope_scaling raises ValueError."""
    t = pd.date_range('2020-01-01', periods=100, freq='D')
    x = np.random.normal(0, 1, 100)

    with pytest.raises(ValueError, match="Invalid `slope_scaling` parameter"):
        power_test(x, t, slopes=[1.0], n_simulations=5, n_surrogates=20, slope_scaling='foobar')
