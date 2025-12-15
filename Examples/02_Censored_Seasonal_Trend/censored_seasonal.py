import numpy as np
import pandas as pd
from MannKenSen import prepare_censored_data, seasonal_trend_test

def main():
    """
    Generate seasonal data with a trend, introduce censoring, and perform
    a seasonal trend analysis.
    """
    # 1. Generate Synthetic Data
    # We will create 20 years of monthly data using a simple numeric time vector
    # to ensure the slope calculation is clear and avoids floating-point issues.
    n_years = 20
    t = np.linspace(2000, 2000 + n_years, n_years * 12, endpoint=False)

    # Create a simple, repeating seasonal pattern for 12 months
    seasonal_pattern = np.tile([5, 8, 12, 18, 25, 30, 32, 30, 25, 18, 10, 6], n_years)

    # Create a clear linear trend
    slope_per_year = 2.0
    linear_trend = slope_per_year * (t - t[0])

    # Combine patterns with noise
    noise = np.random.normal(0, 4, len(t))
    x_raw_numeric = 20 + seasonal_pattern + linear_trend + noise

    # 2. Introduce Censoring
    detection_limit = 45
    x_mixed = [f"<{detection_limit}" if val < detection_limit else val for val in x_raw_numeric]

    # 3. Pre-process the Censored Data
    x_prepared = prepare_censored_data(x_mixed)

    # 4. Perform Seasonal Trend Analysis
    # Since `t` is numeric (in years), we specify a `period` of 1 to represent one full year.
    # The function will internally create 12 seasons based on the data's position within each year.
    plot_path = "Examples/02_Censored_Seasonal_Trend/censored_seasonal_plot.png"
    result = seasonal_trend_test(x=x_prepared, t=t, period=1, plot_path=plot_path)

    # 5. Print the Results
    # The slope is already in units per year because our time vector is in years.
    print("Censored Seasonal Trend Analysis Results:")
    print(f"  Trend: {result.trend}")
    print(f"  P-value: {result.p:.4f}")
    print(f"  Annual Sen's Slope: {result.slope:.4f}")
    print(f"  Kendall's Tau: {result.Tau:.4f}")
    print(f"  Plot saved to: {plot_path}")

if __name__ == "__main__":
    main()
