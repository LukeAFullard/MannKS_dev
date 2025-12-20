import datetime
import os
import numpy as np
import pandas as pd
import pytest

# Import internal functions to be tested
from MannKenSen._helpers import (
    _preprocessing,
    _aggregate_censored_median,
    _value_for_time_increment,
    _aggregate_by_group
)

# --- Tests for _preprocessing ---

def test_preprocessing_datetime_object_array():
    """Test _preprocessing with an object array of datetime.datetime."""
    t_obj = np.array([datetime.datetime(2020, 1, 1), datetime.datetime(2021, 1, 1)])
    t_numeric, ndim = _preprocessing(t_obj)
    assert ndim == 1
    assert t_numeric.dtype == float
    assert t_numeric[0] == datetime.datetime(2020, 1, 1).timestamp()

def test_preprocessing_2d_array():
    """Test _preprocessing with a 2D numpy array which should be flattened."""
    x_2d = np.array([[1], [2], [3]])
    x_flat, ndim = _preprocessing(x_2d)
    assert ndim == 1
    assert x_flat.ndim == 1
    np.testing.assert_array_equal(x_flat, np.array([1, 2, 3]))

# --- Tests for _aggregate_censored_median ---

def test_aggregate_censored_median_empty_mode():
    """
    Test _aggregate_censored_median when the mode of cen_type is empty.
    This happens when censored data points have NaN cen_type values.
    """
    group = pd.DataFrame({
        'value': [1, 5, 10],
        'censored': [False, True, False],
        'cen_type': ['not', np.nan, 'not'],
        't_original': [1, 2, 3],
        't': [1, 2, 3]
    })
    result_df = _aggregate_censored_median(group, is_datetime=False)
    assert len(result_df) == 1
    assert result_df['value'].iloc[0] == 5.0
    assert not result_df['censored'].iloc[0]
    assert result_df['cen_type'].iloc[0] == 'not'


# --- Tests for _value_for_time_increment ---

def test_value_for_time_increment_numeric_time():
    """Test _value_for_time_increment with numeric time data."""
    df = pd.DataFrame({
        't': np.array([2000.1, 2000.8, 2001.5, 2001.6]),
        'cycle': [2000, 2000, 2001, 2001],
        'season': [1, 1, 1, 1]
    })
    result_df = _value_for_time_increment(df, is_datetime=False, season_type='month')
    assert len(result_df) == 2
    assert 2000.1 in result_df['t'].values
    assert 2001.5 in result_df['t'].values

# --- Tests for _aggregate_by_group ---

def test_aggregate_by_group_middle_lwp_numeric():
    """Test _aggregate_by_group with 'middle_lwp' and numeric time."""
    group = pd.DataFrame({
        'value': [10, 20, 30],
        't': [2000.1, 2000.5, 2000.9]
    })
    result_df = _aggregate_by_group(group, agg_method='middle_lwp', is_datetime=False)
    assert len(result_df) == 1
    assert result_df['value'].iloc[0] == 20
    assert result_df['t'].iloc[0] == 2000.5
