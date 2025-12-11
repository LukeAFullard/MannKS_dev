import pytest
import numpy as np
import pandas as pd
from MannKenSen._utils import _aggregate_censored_median

def test_aggregate_censored_median_lwp_logic():
    """
    Tests that the censored median aggregation follows the LWP-TRENDS logic.

    This test case is designed to fail with the old implementation and pass
    with the corrected one. It checks an even-sized group where the median
    value is different from any of the individual observations and the
    censored status must be determined by comparing the calculated median
    to the maximum censored value in the group.
    """
    # Test Data: [1, <3, 8, 10]
    # Numerical Median = (3 + 8) / 2 = 5.5
    # Max Censored Value = 3
    # LWP Logic: Is median (5.5) <= max_censored (3)? => False.
    # The aggregated median should be 5.5 and NOT censored.
    # The OLD logic would pick the 3rd element (8) and report a value of 8
    # with a censored status of False.
    group_data = pd.DataFrame({
        'value': [1.0, 3.0, 8.0, 10.0],
        'censored': [False, True, False, False],
        'cen_type': ['not', 'lt', 'not', 'not'],
        't_original': [1, 2, 3, 4], # Dummy time values
        't': [1, 2, 3, 4]
    })

    result_df = _aggregate_censored_median(group_data, is_datetime=False)

    # Expected results based on LWP logic
    expected_value = 5.5
    expected_censored = False

    # Assertions
    assert result_df is not None
    assert 'value' in result_df.columns
    assert 'censored' in result_df.columns
    assert np.isclose(result_df['value'].iloc[0], expected_value)
    assert result_df['censored'].iloc[0] == expected_censored
