import numpy as np
import sys
from MannKenSen import prepare_censored_data, seasonal_trend_test

def main():
    """
    Generate censored seasonal data and perform a trend analysis using
    LWP-TRENDS R script compatible settings for validation.
    """
    # 1. Generate Synthetic Data
    n_years = 20
    t = np.linspace(2000, 2000 + n_years, n_years * 12, endpoint=False)
    seasonal_pattern = np.tile([5, 8, 12, 18, 25, 30, 32, 30, 25, 18, 10, 6], n_years)
    slope_per_year = 2.0
    linear_trend = slope_per_year * (t - t[0])
    np.random.seed(123)
    noise = np.random.normal(0, 4, len(t))
    x_raw_numeric = 20 + seasonal_pattern + linear_trend + noise

    # 2. Introduce Censoring
    detection_limit = 35
    x_mixed = [f"<{detection_limit}" if val < detection_limit else val for val in x_raw_numeric]
    x_prepared = prepare_censored_data(x_mixed)

    # 3. Perform Trend Analysis with LWP-compatible settings
    plot_path = "validation/02_censored_seasonal_comparison/py_censored_seasonal_plot.png"
    result = seasonal_trend_test(
        x=x_prepared,
        t=t,
        period=12,
        plot_path=plot_path,
        sens_slope_method='lwp',
        mk_test_method='lwp',
        tie_break_method='lwp',
        ci_method='lwp'
    )

    # 4. Print the Results to a file
    original_stdout = sys.stdout
    with open('validation/02_censored_seasonal_comparison/py_censored_seasonal_output.txt', 'w') as f:
        sys.stdout = f
        print("--- Python Censored Seasonal Trend Analysis (LWP-Compatible) ---")
        print(f"  Trend: {result.trend}")
        print(f"  P-value: {result.p:.4f}")
        print(f"  Z-statistic: {result.z:.4f}")
        print(f"  S-statistic: {result.s}")
        print(f"  Variance of S: {result.var_s:.4f}")
        print(f"  Slope: {result.slope:.4f}")
        print(f"  Lower CI: {result.lower_ci:.4f}")
        print(f"  Upper CI: {result.upper_ci:.4f}")
    sys.stdout = original_stdout

    print("Python validation script for example 2 executed successfully.")
    print("Output saved to validation/02_censored_seasonal_comparison/")

if __name__ == "__main__":
    main()
