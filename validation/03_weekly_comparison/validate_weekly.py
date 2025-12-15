import numpy as np
import sys
import pandas as pd
from MannKenSen import seasonal_trend_test

def main():
    """
    Generate weekly seasonal data and perform a trend analysis using
    LWP-TRENDS R script compatible settings for validation.
    """
    # 1. Generate Synthetic Data
    n_years = 5
    t = pd.to_datetime(pd.date_range(start='2018-01-01', periods=365 * n_years, freq='D'))

    day_of_week = t.dayofweek
    weekly_pattern = np.array([-15 if day in (5, 6) else 5 for day in day_of_week])
    np.random.seed(42)
    noise = np.random.normal(0, 4, len(t))
    x = 100 + weekly_pattern + noise

    # 2. Perform Trend Analysis with LWP-compatible settings
    plot_path = "validation/03_weekly_comparison/py_weekly_plot.png"
    result = seasonal_trend_test(
        x, t,
        period=7,
        season_type='day_of_week',
        plot_path=plot_path,
        mk_test_method='lwp',
        tie_break_method='lwp',
        ci_method='lwp'
    )

    # 3. Print the Results to a file
    original_stdout = sys.stdout
    with open('validation/03_weekly_comparison/py_weekly_output.txt', 'w') as f:
        sys.stdout = f
        print("--- Python Weekly Seasonal Trend Analysis (LWP-Compatible) ---")
        print(f"  Trend: {result.trend}")
        print(f"  P-value: {result.p:.4f}")
        print(f"  Z-statistic: {result.z:.4f}")
        print(f"  S-statistic: {result.s}")
        print(f"  Variance of S: {result.var_s:.4f}")
        print(f"  Slope: {result.slope:.4f}")
        print(f"  Lower CI: {result.lower_ci:.4f}")
        print(f"  Upper CI: {result.upper_ci:.4f}")
    sys.stdout = original_stdout

    print("Python validation script for example 3 executed successfully.")
    print("Output saved to validation/03_weekly_comparison/")

if __name__ == "__main__":
    main()
