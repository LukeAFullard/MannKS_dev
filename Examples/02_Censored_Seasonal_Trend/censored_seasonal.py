import numpy as np
import pandas as pd
from MannKenSen import prepare_censored_data, seasonal_trend_test

def main():
    """
    Generate seasonal data with a trend, introduce censoring, and perform
    a seasonal trend analysis.
    """
    # 1. Generate Synthetic Data
    n_years = 20
    t = np.linspace(2000, 2000 + n_years, n_years * 12, endpoint=False)
    seasonal_pattern = np.tile([5, 8, 12, 18, 25, 30, 32, 30, 25, 18, 10, 6], n_years)
    slope_per_year = 2.0
    linear_trend = slope_per_year * (t - t[0])
    np.random.seed(123) # Set seed for reproducibility
    noise = np.random.normal(0, 4, len(t))
    x_raw_numeric = 20 + seasonal_pattern + linear_trend + noise

    # 2. Introduce Censoring
    # A lower limit is chosen to censor less data than the original example
    detection_limit = 35
    x_mixed = [f"<{detection_limit}" if val < detection_limit else val for val in x_raw_numeric]

    # 3. Pre-process the Censored Data
    x_prepared = prepare_censored_data(x_mixed)

    # 4. Perform Seasonal Trend Analysis with both methods
    plot_path = "Examples/02_Censored_Seasonal_Trend/censored_seasonal_plot.png"

    # Method 1: 'nan' (Default, statistically neutral)
    result_nan = seasonal_trend_test(x=x_prepared,
                                     t=t,
                                     period=12, # Use 12 for monthly data
                                     plot_path=plot_path,
                                     sens_slope_method='nan')

    # Method 2: 'lwp' (LWP-TRENDS R script compatibility)
    result_lwp = seasonal_trend_test(x=x_prepared,
                                     t=t,
                                     period=12, # Use 12 for monthly data
                                     plot_path=None, # Don't overwrite plot
                                     sens_slope_method='lwp')

    # 5. Print the Results for Comparison
    print("--- Censored Seasonal Trend Analysis Results ---")
    print("\nThis example compares two methods for calculating Sen's slope with")
    print("censored data. The underlying 'true' slope of the generated data is 2.0.")

    print("\n--- Method 1: sens_slope_method='nan' (Default) ---")
    print("This method is statistically neutral, excluding ambiguous censored slopes.")
    print(f"  Classification: {result_nan.classification}")
    print(f"  Trend: {result_nan.trend}")
    print(f"  P-value: {result_nan.p:.4f}")
    print(f"  Slope: {result_nan.slope:.2f} ({result_nan.lower_ci:.2f}, {result_nan.upper_ci:.2f})")
    print(f"  Analysis Notes: {result_nan.analysis_notes if result_nan.analysis_notes else 'None'}")

    print("\n--- Method 2: sens_slope_method='lwp' (LWP-TRENDS compatibility) ---")
    print("This method sets ambiguous censored slopes to 0, biasing the result towards zero.")
    print(f"  Classification: {result_lwp.classification}")
    print(f"  Trend: {result_lwp.trend}")
    print(f"  P-value: {result_lwp.p:.4f}")
    print(f"  Slope: {result_lwp.slope:.2f} ({result_lwp.lower_ci:.2f}, {result_lwp.upper_ci:.2f})")
    print(f"  Analysis Notes: {result_lwp.analysis_notes if result_lwp.analysis_notes else 'None'}")

    print(f"\nPlot for the default ('nan') method saved to: {plot_path}")

if __name__ == "__main__":
    main()
