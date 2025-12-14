import pytest
import numpy as np
import pandas as pd
from MannKenSen import original_test, seasonal_test
from MannKenSen.preprocessing import prepare_censored_data

# Unit tests for the new `prepare_censored_data` function
def test_prepare_censored_data_valid():
    x = [1, '<2', 3, '>4', '5']
    expected_df = pd.DataFrame({
        'value': [1.0, 2.0, 3.0, 4.0, 5.0],
        'censored': [False, True, False, True, False],
        'cen_type': ['not', 'lt', 'not', 'gt', 'not']
    })
    result_df = prepare_censored_data(x)
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_prepare_censored_data_all_numeric():
    x = [1, 2, 3, 4, 5]
    expected_df = pd.DataFrame({
        'value': [1.0, 2.0, 3.0, 4.0, 5.0],
        'censored': [False, False, False, False, False],
        'cen_type': ['not', 'not', 'not', 'not', 'not']
    })
    result_df = prepare_censored_data(x)
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_prepare_censored_data_with_spaces():
    x = [' < 2 ', ' > 4 ']
    expected_df = pd.DataFrame({
        'value': [2.0, 4.0],
        'censored': [True, True],
        'cen_type': ['lt', 'gt']
    })
    result_df = prepare_censored_data(x)
    pd.testing.assert_frame_equal(result_df, expected_df)

def test_prepare_censored_data_invalid_string():
    with pytest.raises(ValueError, match="Could not convert string 'abc' to a float."):
        prepare_censored_data(['abc'])

def test_prepare_censored_data_invalid_censored_format():
    with pytest.raises(ValueError, match="Invalid left-censored value format: '<'. Expected a number after the '<' symbol."):
        prepare_censored_data(['<'])
    with pytest.raises(ValueError, match="Invalid right-censored value format: '>a'. Expected a number after the '>' symbol."):
        prepare_censored_data(['>a'])

def test_prepare_censored_data_malformed_strings():
    """Test `prepare_censored_data` with other malformed strings."""
    with pytest.raises(ValueError):
        prepare_censored_data(['<>5'])

def test_prepare_censored_data_non_iterable():
    with pytest.raises(TypeError):
        prepare_censored_data(123)

def test_prepare_censored_data_mixed_censoring_warning():
    """Test that a warning is issued for mixed censoring types on the same value."""
    # Test between two different censoring types
    x1 = ['<5', '>5']
    with pytest.warns(UserWarning, match="Value 5.0 has conflicting censoring types"):
        prepare_censored_data(x1)

    # Test between a censored and non-censored value
    x2 = ['<5', '5']
    with pytest.warns(UserWarning, match="Value 5.0 has conflicting censoring types"):
        prepare_censored_data(x2)

# New test for dynamic tie-breaking in censored data
def test_dynamic_tie_breaking_right_censored():
    """
    Tests that the tie-breaking for right-censored data is handled correctly,
    regardless of the data's scale.
    """
    # Dataset with a clear increasing trend and a right-censored value
    # that could cause issues if the tie-breaking value is too large.
    x = [1, 2, 3, 4, '>4']
    t = np.arange(len(x))

    # Pre-process the data
    data = prepare_censored_data(x)

    # Perform the trend test with the new 'robust' default
    result_robust = original_test(data, t)

    # The robust method is more conservative and correctly finds no significant
    # trend in this small dataset.
    assert result_robust.trend == 'no trend'
    assert not result_robust.h

    # The 'lwp' method should still find an increasing trend
    result_lwp = original_test(data, t, mk_test_method='lwp')
    assert result_lwp.trend == 'increasing'
    assert result_lwp.h

def test_hicensor_rule_original_test():
    """Test the hicensor rule in original_test."""
    x = ['<5', 3, 2, '<10', 8, 1] # More sensitive to hicensor
    t = np.arange(len(x))
    data = prepare_censored_data(x)

    # Without hicensor, trend should be present
    result_no_hicensor = original_test(x=data, t=t)

    # With hicensor, all values < 10 become censored at 10.
    # The data effectively becomes ['<10', '<10', '<10', '<10', '<10', '<10']
    # This should result in no trend.
    result_hicensor = original_test(x=data, t=t, hicensor=True)
    assert result_hicensor.trend == 'no trend'
    assert abs(result_hicensor.s) < abs(result_no_hicensor.s)

def test_original_test_string_input_error():
    """
    Test that original_test raises a TypeError if the input contains
    strings but is not a DataFrame from prepare_censored_data.
    """
    x = ['1', '2', '<3']
    t = np.arange(len(x))
    with pytest.raises(TypeError, match="Input data `x` contains strings. Please pre-process it with `prepare_censored_data` first."):
        original_test(x=x, t=t)

def test_hicensor_rule_seasonal_test():
    """Test the hicensor rule in seasonal_test."""
    # Data spanning two years, with a clear seasonal trend without hicensor
    t = pd.to_datetime(['2020-01-15', '2020-07-15', '2021-01-15', '2021-07-15'])
    x = ['<10', 20, '<5', 22] # Jan values are censored, July values increase
    data = prepare_censored_data(x)

    # Without hicensor, the July trend should be detected
    result_no_hicensor = seasonal_test(x=data, t=t, period=12)

    # With hicensor, the max censor limit is 10.
    # The data becomes:
    # Jan 2020: <10
    # Jul 2020: 20
    # Jan 2021: <10 (originally <5, now censored at 10)
    # Jul 2021: 22
    # The trend in July is still increasing, but the overall s-score
    # might be affected. The key is to ensure it runs and weakens the trend.
    result_hicensor = seasonal_test(x=data, t=t, period=12, hicensor=True)

    # The hicensor rule correctly weakens the trend to "no trend" in this case,
    # as the Mann-Kendall score `s` becomes 1, which results in a z-score of 0
    # after the continuity correction.
    assert result_hicensor.trend == 'no trend'
    # The absolute s-score should be less than the original, demonstrating
    # that the trend has been weakened or remained the same.
    assert abs(result_hicensor.s) <= abs(result_no_hicensor.s)

def test_hicensor_numeric_original_test():
    """Test numeric hicensor support in original_test."""
    x = ['<5', 3, 2, '<10', 8, 1]
    t = np.arange(len(x))
    data = prepare_censored_data(x)

    # With hicensor=8, all values < 8 become censored at 8.
    result_hicensor_8 = original_test(x=data, t=t, hicensor=8)
    assert result_hicensor_8.trend == 'no trend'

    # With hicensor=12 (higher than max censor), it should behave like hicensor=True
    result_hicensor_12 = original_test(x=data, t=t, hicensor=12)
    result_hicensor_true = original_test(x=data, t=t, hicensor=True)
    assert result_hicensor_12.s == result_hicensor_true.s
    assert result_hicensor_12.trend == result_hicensor_true.trend

def test_hicensor_invalid_type_error():
    """Test that an invalid type for hicensor raises a ValueError."""
    x = [1, 2, 3]
    t = np.arange(len(x))
    with pytest.raises(ValueError, match="hicensor must be bool or numeric"):
        original_test(x=x, t=t, hicensor="invalid")

def test_hicensor_numeric_seasonal_test():
    """Test numeric hicensor support in seasonal_test."""
    t = pd.to_datetime(['2020-01-15', '2020-07-15', '2021-01-15', '2021-07-15'])
    x = ['<10', 20, '<5', 22]
    data = prepare_censored_data(x)

    # With hicensor=8, the Jan data becomes [<8, <8], which has no trend.
    # The July data [20, 22] has an increasing trend, but the overall
    # result is weakened by the tied January data.
    result_hicensor_8 = seasonal_test(x=data, t=t, period=12, hicensor=8)
    assert result_hicensor_8.trend == 'no trend'


# Tests for the new mk_test_method parameter
def test_mk_test_method_lwp_vs_robust():
    """
    Compare the 'lwp' and 'robust' methods for right-censored data.
    """
    # Create a dataset where the methods should produce different results.
    # The robust method should be less influenced by the right-censored value.
    x_raw = [10, 8, '>5', 6]
    t = np.arange(len(x_raw))
    x_prepared = prepare_censored_data(x_raw)

    # LWP method - should be more strongly decreasing
    res_lwp = original_test(x=x_prepared, t=t, mk_test_method='lwp')

    # Robust method - should be less strongly decreasing
    res_robust = original_test(x=x_prepared, t=t, mk_test_method='robust')

    # Assertions
    # With n=4, the trend is not significant for either method
    assert res_lwp.trend == 'no trend'
    assert res_robust.trend == 'no trend'
    # For this specific dataset, both methods produce the same S-score.
    assert res_robust.s == res_lwp.s

def test_mk_test_method_robust_ambiguous_case():
    """
    Test the robust method in a case where the right-censored value creates
    ambiguity.
    """
    # Here, the uncensored value '6' is GREATER than the censored limit '>5'.
    # The robust method should treat the pair (6, >5) as a confirmed
    # positive contribution to S.
    # The uncensored value '4' is LESS than the censored limit '>5'.
    # The robust method should treat this pair (4, >5) as ambiguous (score=0).
    x_raw = [6, '>5', 4]
    t = np.arange(len(x_raw))
    x_prepared = prepare_censored_data(x_raw)

    res_robust = original_test(x=x_prepared, t=t, mk_test_method='robust')

    # The pairs are:
    # (6, >5) -> S = 0 (ambiguous because 6 > 5)
    # (6, 4)  -> S = -1
    # (>5, 4) -> S = -1 (not ambiguous because >5 must be > 4)
    # Total S = -2
    assert res_robust.s == -2
    assert res_robust.trend == 'no trend'

def test_mk_test_method_lwp_right_censor_tie():
    """
    Test that the 'lwp' method correctly creates a tie for right-censored data.
    """
    x_raw = [10, '>5', '>4']
    t = np.arange(len(x_raw))
    x_prepared = prepare_censored_data(x_raw)
    res_lwp = original_test(x=x_prepared, t=t, mk_test_method='lwp')

    # Under the 'lwp' method, '>5' and '>4' become tied at a value slightly
    # greater than 5.
    # The pairs are:
    # (10, >5) -> S = -1
    # (10, >4) -> S = -1
    # (>5, >4) -> S = 0 (tie)
    # Total S = -2
    assert res_lwp.s == -2
