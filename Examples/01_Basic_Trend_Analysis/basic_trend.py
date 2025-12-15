import numpy as np
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

    # 2. Perform Trend Analysis
    plot_path = "Examples/01_Basic_Trend_Analysis/basic_trend_plot.png"
    result = trend_test(x, t, plot_path=plot_path)

    # 3. Print the Results
    print("--- Basic Trend Analysis Results ---")
    print(f"  Classification: {result.classification}")
    print(f"  Trend: {result.trend}")
    print(f"  P-value: {result.p:.4f}")
    print(f"  Slope: {result.slope:.2f} ({result.lower_ci:.2f}, {result.upper_ci:.2f})")
    print(f"  Analysis Notes: {result.analysis_notes if result.analysis_notes else 'None'}")
    print(f"\n  Plot saved to: {plot_path}")

if __name__ == "__main__":
    main()
