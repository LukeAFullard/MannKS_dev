
import pandas as pd
import numpy as np
from MannKenSen._helpers import _value_for_time_increment

def test_aggregation_equivalence():
    # Setup test data: Two dates in Jan 2020.
    # Midpoint of Jan 2020 is roughly Jan 16 12:00.
    # Case 1: Early and Late.
    dates = pd.to_datetime(['2020-01-02', '2020-01-25'])
    values = [10, 20]
    df = pd.DataFrame({'t_original': dates, 'value': values, 't': dates.astype(np.int64) // 10**9})

    # Group key for "2020-01"
    group_key = pd.Series([1, 1])

    # Run aggregation - using 'M' instead of 'ME' because pandas < 2.2 strictness might vary, or vice versa.
    # The error message said "please use 'M' instead of 'ME'".
    result = _value_for_time_increment(df, group_key, 'M')

    print("--- Case 1: Jan 2 vs Jan 25 ---")
    print(f"Midpoint should be approx Jan 16")
    print(f"Jan 2 dist: ~14 days. Jan 25 dist: ~9 days.")
    print(f"Expected: Jan 25 (value 20)")
    print(result[['t_original', 'value']])

    # Case 2: Tie breaking
    # Midpoint of Jan 2020 (31 days) starts at Jan 1 00:00, ends Jan 31 23:59:59...
    # Period: 2020-01-01 to 2020-01-31
    # Midpoint: Jan 16 12:00:00 (Leap year doesn't affect month length)

    # Dates equidistant: Jan 16 11:00 vs Jan 16 13:00
    dates_tie = pd.to_datetime(['2020-01-16 11:00:00', '2020-01-16 13:00:00'])
    df_tie = pd.DataFrame({'t_original': dates_tie, 'value': [100, 200], 't': dates_tie.astype(np.int64) // 10**9})

    result_tie = _value_for_time_increment(df_tie, group_key, 'M')

    print("\n--- Case 2: Tie Breaking (11:00 vs 13:00) ---")
    print(f"Midpoint: Jan 16 12:00")
    print(f"Expected: First one (Jan 16 11:00) if using idxmin() on ordered index?")
    print(result_tie[['t_original', 'value']])

    # Case 3: Numeric Time Vector
    # MKS currently converts to datetime. Let's see what happens with pure numbers.
    print("\n--- Case 3: Numeric Time Vector ---")
    df_num = pd.DataFrame({'t_original': [1.1, 1.9], 'value': [1, 2], 't': [1.1, 1.9]})
    group_key_num = pd.Series([1, 1])
    try:
        # Period 'ME' (Month End) makes no sense for numbers 1.1, 1.9 if they aren't seconds.
        # But _value_for_time_increment expects 'period' string.
        # If we pass dummy period, it will try to use it on t_original.
        res_num = _value_for_time_increment(df_num, group_key_num, 'Y')
        print(res_num)
    except Exception as e:
        print(f"Error as expected: {e}")

if __name__ == "__main__":
    test_aggregation_equivalence()
