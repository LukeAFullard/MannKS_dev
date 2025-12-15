import numpy as np
import pandas as pd
from MannKenSen import seasonal_trend_test

def main():
    """
    Demonstrate the effect of the `agg_method` parameter in `seasonal_trend_test`
    when multiple observations exist within the same season.
    """
    # 1. Generate Synthetic Data with Duplicates
    np.random.seed(42) # Set seed for reproducibility
    n_years = 15
    base_time = np.linspace(2000, 2000 + n_years, n_years * 12, endpoint=False)
    base_x = 1.5 * (base_time - base_time[0]) + np.random.normal(0, 5, len(base_time))

    extra_time = np.array([2002.1, 2005.5, 2005.55, 2010.8])
    extra_x = 1.5 * (extra_time - base_time[0]) + np.random.normal(0, 5, len(extra_time))

    t = np.sort(np.concatenate([base_time, extra_time]))
    x = np.concatenate([base_x, extra_x])[np.argsort(np.concatenate([base_time, extra_time]))]

    # 2. Perform Trend Analysis with Different Aggregation Methods
    print("--- Running Analysis with Different Aggregation Methods ---")

    # Method 1: No Aggregation ('none')
    result_none = seasonal_trend_test(x, t, period=12, agg_method='none')
    print("\nResult with agg_method='none':")
    print(f"  Classification: {result_none.classification}")
    print(f"  Slope: {result_none.slope:.2f} ({result_none.lower_ci:.2f}, {result_none.upper_ci:.2f})")
    print(f"  S-statistic: {result_none.s}")
    print(f"  Analysis Notes: {result_none.analysis_notes if result_none.analysis_notes else 'None'}")


    # Method 2: Median Aggregation ('median')
    result_median = seasonal_trend_test(x, t, period=12, agg_method='median')
    print("\nResult with agg_method='median':")
    print(f"  Classification: {result_median.classification}")
    print(f"  Slope: {result_median.slope:.2f} ({result_median.lower_ci:.2f}, {result_median.upper_ci:.2f})")
    print(f"  S-statistic: {result_median.s}")
    print(f"  Analysis Notes: {result_median.analysis_notes if result_median.analysis_notes else 'None'}")


    # 3. Save a Plot for the Median Aggregation Case
    plot_path = "Examples/04_Aggregation_Example/aggregation_plot.png"
    seasonal_trend_test(x, t, period=12, agg_method='median', plot_path=plot_path)
    print(f"\nPlot for the 'median' aggregation method saved to: {plot_path}")

if __name__ == "__main__":
    main()
