import numpy as np
import sys
from MannKenSen import trend_test

def main():
    """
    Generate a simple linear time series with noise and perform a trend analysis
    using LWP-TRENDS R script compatible settings.
    """
    # 1. Generate Synthetic Data
    np.random.seed(42)
    t = np.arange(2000, 2020, dtype=float)
    slope = 2.5
    intercept = 10
    noise = np.random.normal(0, 5, len(t))
    x = slope * (t - t[0]) + intercept + noise

    # 2. Perform Trend Analysis with LWP-compatible settings
    plot_path = "validation/01_basic_comparison/py_basic_plot.png"
    result = trend_test(
        x, t,
        plot_path=plot_path,
        tie_break_method='lwp',
        ci_method='lwp'
    )

    # 3. Print the Results
    # Redirect print to a file
    original_stdout = sys.stdout
    with open('validation/01_basic_comparison/py_basic_output.txt', 'w') as f:
        sys.stdout = f
        print("--- Python Basic Trend Analysis (LWP-Compatible) ---")
        print(f"  Trend: {result.trend}")
        print(f"  P-value: {result.p:.4f}")
        print(f"  Z-statistic: {result.z:.4f}")
        print(f"  S-statistic: {result.s}")
        print(f"  Variance of S: {result.var_s:.4f}")
        print(f"  Slope: {result.slope:.4f}")
        print(f"  Lower CI: {result.lower_ci:.4f}")
        print(f"  Upper CI: {result.upper_ci:.4f}")
    sys.stdout = original_stdout

    print("Python validation script for example 1 executed successfully.")
    print("Output saved to validation/01_basic_comparison/")


if __name__ == "__main__":
    main()
