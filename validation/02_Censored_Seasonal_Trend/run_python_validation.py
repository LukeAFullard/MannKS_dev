import numpy as np
import pandas as pd
from MannKenSen import prepare_censored_data, seasonal_trend_test

def main():
    """
    Generate seasonal data with a trend, introduce censoring, perform
    a seasonal trend analysis, and save the data for R validation.
    """
    # 1. Generate Synthetic Data
    n_years = 20
    # Generate timestamps as fractional years
    t = np.linspace(2000, 2000 + n_years, n_years * 12, endpoint=False)
    seasonal_pattern = np.tile([5, 8, 12, 18, 25, 30, 32, 30, 25, 18, 10, 6], n_years)
    slope_per_year = 2.0
    linear_trend = slope_per_year * (t - t[0])
    np.random.seed(123) # Set seed for reproducibility
    noise = np.random.normal(0, 4, len(t))
    x_raw_numeric = 20 + seasonal_pattern + linear_trend + noise

    # 2. Introduce Censoring
    detection_limit = 35
    x_mixed = [f"<{detection_limit}" if val < detection_limit else val for val in x_raw_numeric]

    # 3. Save Data for Validation
    # Create a DataFrame for validation output
    df = pd.DataFrame({'time': t, 'value': x_mixed})
    output_csv_path = "validation/02_Censored_Seasonal_Trend/validation_data.csv"
    df.to_csv(output_csv_path, index=False)
    print(f"Validation data saved to: {output_csv_path}")


    # 4. Pre-process the Censored Data for Python Analysis
    x_prepared = prepare_censored_data(df['value']) # Pass the series directly

    # 5. Perform Seasonal Trend Analysis (LWP-TRENDS compatibility method)
    plot_path = "validation/02_Censored_Seasonal_Trend/censored_seasonal_plot.png"

    result_lwp = seasonal_trend_test(x=x_prepared,
                                     t=df['time'], # Use time from the dataframe
                                     period=12, # Use 12 for monthly data
                                     plot_path=plot_path,
                                     sens_slope_method='lwp')

    # 6. Print the Python Results
    print("\n--- Python `MannKenSen` Package Results ---")
    print("Method: sens_slope_method='lwp' (for LWP-TRENDS compatibility)")
    print(f"  Classification: {result_lwp.classification}")
    print(f"  Trend: {result_lwp.trend}")
    print(f"  P-value: {result_lwp.p:.4f}")
    print(f"  Slope: {result_lwp.slope:.4f}")
    print(f"  Lower CI: {result_lwp.lower_ci:.4f}")
    print(f"  Upper CI: {result_lwp.upper_ci:.4f}")
    print(f"  Analysis Notes: {result_lwp.analysis_notes if result_lwp.analysis_notes else 'None'}")
    print(f"\nPlot saved to: {plot_path}")

if __name__ == "__main__":
    main()
