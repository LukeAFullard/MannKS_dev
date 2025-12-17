import numpy as np
import pandas as pd
from MannKenSen import seasonal_trend_test

def main():
    """
    Validation script for the `agg_method` parameter.

    This script generates a synthetic monthly dataset with duplicate observations,
    saves it to a CSV file, and then runs `seasonal_trend_test` with and
    without aggregation to validate the feature against the R script's behavior.
    """
    # 1. Generate Consistent Synthetic Data
    np.random.seed(42)
    n_years = 15

    # Create a clean monthly time series
    dates = pd.date_range(start='2000-01-01', periods=n_years * 12, freq='MS')

    # Create a base trend
    time_as_years = dates.year + dates.month / 12.0
    values = 1.5 * (time_as_years - time_as_years[0]) + np.random.normal(0, 5, len(dates))

    # Add duplicate observations to specific months
    extra_dates = pd.to_datetime(['2002-02-15', '2005-06-10', '2005-06-20', '2010-09-05'])
    extra_time_as_years = extra_dates.year + extra_dates.month / 12.0
    extra_values = 1.5 * (extra_time_as_years - time_as_years[0]) + np.random.normal(0, 5, len(extra_dates))

    # Combine and sort the data
    all_dates = pd.concat([pd.Series(dates), pd.Series(extra_dates)]).sort_values().reset_index(drop=True)
    all_values = np.concatenate([values, extra_values])[pd.concat([pd.Series(dates), pd.Series(extra_dates)]).argsort()]

    # Save data for R validation
    df_to_save = pd.DataFrame({'Date': all_dates, 'Value': all_values})
    df_to_save.to_csv('validation/04_Aggregation_Example/validation_data.csv', index=False)

    # 2. Perform Trend Analysis with Different Aggregation Methods
    print("--- Python: Running Analysis with Different Aggregation Methods ---")

    # Method 1: No Aggregation ('none')
    result_none = seasonal_trend_test(all_values, all_dates, period=12, agg_method='none')
    print("\nResult with agg_method='none':")
    print(f"  Classification: {result_none.classification}")
    print(f"  P-value: {result_none.p:.4f}")
    print(f"  Slope: {result_none.slope:.4f} ({result_none.lower_ci:.4f}, {result_none.upper_ci:.4f})")
    print(f"  Analysis Notes: {result_none.analysis_notes if result_none.analysis_notes else 'None'}")

    # Method 2: Median Aggregation ('median')
    result_median = seasonal_trend_test(all_values, all_dates, period=12, agg_method='median')
    print("\nResult with agg_method='median':")
    print(f"  Classification: {result_median.classification}")
    print(f"  P-value: {result_median.p:.4f}")
    print(f"  Slope: {result_median.slope:.4f} ({result_median.lower_ci:.4f}, {result_median.upper_ci:.4f})")
    print(f"  Analysis Notes: {result_median.analysis_notes if result_median.analysis_notes else 'None'}")

    # 3. Save a Plot for the Median Aggregation Case
    plot_path = "validation/04_Aggregation_Example/aggregation_plot.png"
    seasonal_trend_test(all_values, all_dates, period=12, agg_method='median', plot_path=plot_path)
    print(f"\nPlot for the 'median' aggregation method saved to: {plot_path}")

if __name__ == "__main__":
    main()
