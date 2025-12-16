import numpy as np
import pandas as pd
from MannKenSen import trend_test

def main():
    """
    Generate a simple linear time series with noise and perform a trend analysis.
    """
    # 1. Generate Synthetic Data
    # Set a random seed to ensure the generated noise is the same every time
    # the script is run, which makes the results reproducible.
    np.random.seed(42)
    t = np.arange(2000, 2020, dtype=float)
    slope = 2.5
    intercept = 10
    noise = np.random.normal(0, 5, len(t))
    x = slope * (t - t[0]) + intercept + noise

    # Save data for R validation
    df = pd.DataFrame({'time': t, 'value': x})
    df.to_csv('validation/01_Basic_Trend_Analysis/validation_data.csv', index=False)

    # 2. Perform Trend Analysis (Default 'robust' method)
    plot_path = "validation/01_Basic_Trend_Analysis/basic_trend_plot.png"
    result_robust = trend_test(x, t, plot_path=plot_path)

    # 3. Perform Trend Analysis (LWP Emulation method)
    result_lwp = trend_test(
        x,
        t,
        sens_slope_method='lwp',
        ci_method='lwp',
        tie_break_method='lwp'
    )

    # 4. Print the Results
    print("--- Basic Trend Analysis Results (MannKenSen Default) ---")
    print(f"  Classification: {result_robust.classification}")
    print(f"  Trend: {result_robust.trend}")
    print(f"  Z-statistic: {result_robust.z:.4f}")
    print(f"  P-value: {result_robust.p:.4f}")
    print(f"  Slope: {result_robust.slope:.2f} ({result_robust.lower_ci:.2f}, {result_robust.upper_ci:.2f})")
    print(f"  Analysis Notes: {result_robust.analysis_notes if result_robust.analysis_notes else 'None'}")
    print(f"\n  Plot saved to: {plot_path}")

    print("\n--- Basic Trend Analysis Results (MannKenSen LWP Emulation) ---")
    print(f"  Classification: {result_lwp.classification}")
    print(f"  Trend: {result_lwp.trend}")
    print(f"  Z-statistic: {result_lwp.z:.4f}")
    print(f"  P-value: {result_lwp.p:.4f}")
    print(f"  Slope: {result_lwp.slope:.2f} ({result_lwp.lower_ci:.2f}, {result_lwp.upper_ci:.2f})")
    print(f"  Analysis Notes: {result_lwp.analysis_notes if result_lwp.analysis_notes else 'None'}")

if __name__ == "__main__":
    main()
