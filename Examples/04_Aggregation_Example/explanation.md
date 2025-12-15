# Example 4: Aggregating Time Series Data

In many real-world datasets, you may have more than one sample for a given season (e.g., two water quality samples were taken in January 2010). The `seasonal_trend_test` function provides an `agg_method` parameter to handle these situations.

This example demonstrates the difference between analyzing all data points (`agg_method='none'`) and aggregating them (`agg_method='median'`).

## Steps

1.  **Generate Synthetic Data**: We create a time series with a clear linear trend and add several extra data points to simulate multiple observations within the same season.
2.  **Analyze Without Aggregation**: We run `seasonal_trend_test` with `agg_method='none'`.
3.  **Analyze With Aggregation**: We run the test again with `agg_method='median'`. A plot is saved for this case.
4.  **Compare the Results**: We print the results from both methods to show how the statistics (especially the S-statistic) differ.

## Python Code (`aggregation.py`)

The full Python script for this example is shown below.

```python
import numpy as np
import pandas as pd
from MannKenSen import seasonal_trend_test

def main():
    """
    Demonstrate the effect of the `agg_method` parameter in `seasonal_trend_test`
    when multiple observations exist within the same season.
    """
    # 1. Generate Synthetic Data with Duplicates
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
    result_none = seasonal_trend_test(x, t, period=1, agg_method='none')
    print("\nResult with agg_method='none':")
    print(f"  Classification: {result_none.classification}")
    print(f"  Slope: {result_none.slope:.2f} ({result_none.lower_ci:.2f}, {result_none.upper_ci:.2f})")
    print(f"  S-statistic: {result_none.s}")
    print(f"  Analysis Notes: {result_none.analysis_notes if result_none.analysis_notes else 'None'}")


    # Method 2: Median Aggregation ('median')
    result_median = seasonal_trend_test(x, t, period=1, agg_method='median')
    print("\nResult with agg_method='median':")
    print(f"  Classification: {result_median.classification}")
    print(f"  Slope: {result_median.slope:.2f} ({result_median.lower_ci:.2f}, {result_median.upper_ci:.2f})")
    print(f"  S-statistic: {result_median.s}")
    print(f"  Analysis Notes: {result_median.analysis_notes if result_median.analysis_notes else 'None'}")


    # 3. Save a Plot for the Median Aggregation Case
    plot_path = "Examples/04_Aggregation_Example/aggregation_plot.png"
    seasonal_trend_test(x, t, period=1, agg_method='median', plot_path=plot_path)
    print(f"\nPlot for the 'median' aggregation method saved to: {plot_path}")

if __name__ == "__main__":
    main()
```

## Results

Running the script produces the following output. Both methods correctly identify a **"Highly Likely Increasing"** trend, and their slope estimates are very similar.

The key difference is the **S-statistic**. The `'none'` method has a much larger S-statistic because it considers every pair of points, resulting in a much larger sample size for the test. The `'median'` method first reduces the dataset to one point per season, leading to a smaller S-statistic.

```
--- Running Analysis with Different Aggregation Methods ---

Result with agg_method='none':
  Classification: Highly Likely Increasing
  Slope: 1.42 (1.25, 1.58)
  S-statistic: 10284.0
  Analysis Notes: None

Result with agg_method='median':
  Classification: Highly Likely Increasing
  Slope: 1.39 (1.16, 1.63)
  S-statistic: 95.0
  Analysis Notes: None

Plot for the 'median' aggregation method saved to: Examples/04_Aggregation_Example/aggregation_plot.png
```

### Generated Plot (`agg_method='median'`)

The plot below is for the `'median'` aggregation. The raw data points (including the duplicates) are shown, but the trend line is calculated based on the *median* value within each season.

![Aggregation Example Plot](aggregation_plot.png)
