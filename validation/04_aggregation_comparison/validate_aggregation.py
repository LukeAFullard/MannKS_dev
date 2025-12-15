import numpy as np
import sys
from MannKenSen import seasonal_trend_test

def main():
    """
    Demonstrate the 'middle_lwp' aggregation method using LWP-TRENDS
    R script compatible settings for validation.
    """
    # 1. Generate Synthetic Data
    np.random.seed(42)
    n_years = 15
    base_time = np.linspace(2000, 2000 + n_years, n_years * 12, endpoint=False)
    base_x = 1.5 * (base_time - base_time[0]) + np.random.normal(0, 5, len(base_time))

    extra_time = np.array([2002.1, 2005.5, 2005.55, 2010.8])
    extra_x = 1.5 * (extra_time - base_time[0]) + np.random.normal(0, 5, len(extra_time))

    t = np.sort(np.concatenate([base_time, extra_time]))
    x = np.concatenate([base_x, extra_x])[np.argsort(np.concatenate([base_time, extra_time]))]

    # 2. Perform Trend Analysis with LWP-compatible settings
    plot_path = "validation/04_aggregation_comparison/py_aggregation_plot.png"
    result = seasonal_trend_test(
        x, t,
        period=12,
        agg_method='middle_lwp',
        plot_path=plot_path,
        mk_test_method='lwp',
        tie_break_method='lwp',
        ci_method='lwp'
    )

    # 3. Print the Results to a file
    original_stdout = sys.stdout
    with open('validation/04_aggregation_comparison/py_aggregation_output.txt', 'w') as f:
        sys.stdout = f
        print("--- Python Aggregation Trend Analysis (LWP-Compatible) ---")
        print(f"  Trend: {result.trend}")
        print(f"  P-value: {result.p:.4f}")
        print(f"  Z-statistic: {result.z:.4f}")
        print(f"  S-statistic: {result.s}")
        print(f"  Variance of S: {result.var_s:.4f}")
        print(f"  Slope: {result.slope:.4f}")
        print(f"  Lower CI: {result.lower_ci:.4f}")
        print(f"  Upper CI: {result.upper_ci:.4f}")
    sys.stdout = original_stdout

    print("Python validation script for example 4 executed successfully.")
    print("Output saved to validation/04_aggregation_comparison/")


if __name__ == "__main__":
    main()
