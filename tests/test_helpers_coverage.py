import datetime
import numpy as np
import pandas as pd
import pytest

from MannKenSen._helpers import (
    _preprocessing,
    _missing_values_analysis,
    _aggregate_censored_median,
    _aggregate_by_group
)

def test_preprocessing_datetime_objects():
    """Test _preprocessing with a list of datetime.datetime objects."""
    datetimes = [datetime.datetime(2023, 1, 1), datetime.datetime(2023, 1, 2)]
    processed, ndim = _preprocessing(datetimes)
    assert ndim == 1
    assert processed.dtype == float
    assert np.allclose(processed, [1672531200.0, 1672617600.0])

def test_preprocessing_object_array_of_datetimes():
    """Test _preprocessing with an object array of datetime.datetime objects."""
    datetimes = np.array([datetime.datetime(2023, 1, 1), datetime.datetime(2023, 1, 2)], dtype=object)
    processed, ndim = _preprocessing(datetimes)
    assert ndim == 1
    assert processed.dtype == float
    assert np.allclose(processed, [1672531200.0, 1672617600.0])

def test_preprocessing_2d_single_column():
    """Test _preprocessing with a 2D numpy array with one column."""
    arr = np.array([[1], [2], [3]])
    processed, ndim = _preprocessing(arr)
    assert ndim == 1
    assert processed.ndim == 1
    assert np.array_equal(processed, np.array([1, 2, 3]))

def test_missing_values_analysis_2d():
    """Test _missing_values_analysis with a 2D array."""
    arr = np.array([[1.0, 2.0], [np.nan, 4.0], [5.0, 6.0]])
    processed, length = _missing_values_analysis(arr, method='skip')
    assert length == 2
    assert np.array_equal(processed, np.array([[1.0, 2.0], [5.0, 6.0]]))

def test_aggregate_censored_median_empty_group():
    """Test _aggregate_censored_median with an empty DataFrame."""
    df = pd.DataFrame(columns=['value', 'censored', 'cen_type', 't_original', 't'])
    result = _aggregate_censored_median(df, is_datetime=False)
    assert result.empty

def test_aggregate_by_group_middle_method():
    """Test _aggregate_by_group with the 'middle' method."""
    data = {
        'value': [10, 20, 30],
        't': [100, 102, 108],
        'censored': [False, False, False],
        'cen_type': ['not', 'not', 'not']
    }
    df = pd.DataFrame(data)
    result = _aggregate_by_group(df, 'middle', is_datetime=False)
    assert len(result) == 1
    assert result.iloc[0]['value'] == 20

def test_aggregate_by_group_unknown_method():
    """Test _aggregate_by_group with an unknown aggregation method."""
    data = { 'value': [10, 20], 't': [100, 102], 'censored': [False, False], 'cen_type': ['not', 'not'] }
    df = pd.DataFrame(data)
    result = _aggregate_by_group(df, 'unknown_method', is_datetime=False)
    # Should return the original group
    pd.testing.assert_frame_equal(df, result)
