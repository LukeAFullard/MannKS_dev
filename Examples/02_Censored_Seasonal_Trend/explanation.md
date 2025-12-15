# Example 2: Seasonal Trend with Censored Data

This example demonstrates a more advanced use case involving both seasonality and censored data. We will generate a time series that has a clear seasonal pattern, introduce left-censored data (values below a detection limit), and then use the `prepare_censored_data` and `seasonal_trend_test` functions to perform the analysis.

A key feature of this example is the comparison between two different methods for handling censored data in the Sen's slope calculation, highlighting how methodological choices can impact the results.

## Steps

1.  **Generate Synthetic Data**: We create a time series with a repeating 12-month seasonal pattern and a steady increasing linear trend (the "true" slope is **2.0**). A random seed is set to ensure the noise is the same every time, making the example reproducible.
2.  **Introduce Censoring**: We simulate a detection limit by converting all numeric values below `35` into censored strings (e.g., `"<35"`). This lower limit censors less data than the original version of this example, providing a more realistic scenario.
3.  **Pre-process Data**: The mixed array of numbers and strings is passed to the `prepare_censored_data` utility.
4.  **Perform Trend Analysis (Two Methods)**: We run `seasonal_trend_test` twice, ensuring we set `period=12` to correctly account for the monthly seasonality.
    *   First, with the default `sens_slope_method='nan'`, which is a statistically neutral approach. A plot is saved for this result.
    *   Second, with `sens_slope_method='lwp'`, which mimics the behavior of the LWP-TRENDS R script for compatibility.
5.  **Review and Compare the Output**: We print the results from both methods to analyze their differences.

## Python Code (`censored_seasonal.py`)

The full Python script for this example is shown below. Note the call to `np.random.seed(123)` which ensures this example is fully reproducible.

```python
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
```

## Results and Interpretation

The script produces the following output, which we will analyze in detail.

```
--- Censored Seasonal Trend Analysis Results ---

This example compares two methods for calculating Sen's slope with
censored data. The underlying 'true' slope of the generated data is 2.0.

--- Method 1: sens_slope_method='nan' (Default) ---
This method is statistically neutral, excluding ambiguous censored slopes.
  Classification: Highly Likely Increasing
  Trend: increasing
  P-value: 0.0000
  Slope: 1.81 (1.47, 2.15)
  Analysis Notes: None

--- Method 2: sens_slope_method='lwp' (LWP-TRENDS compatibility) ---
This method sets ambiguous censored slopes to 0, biasing the result towards zero.
  Classification: Highly Likely Increasing
  Trend: increasing
  P-value: 0.0000
  Slope: 1.31 (0.87, 1.65)
  Analysis Notes: ['WARNING: Sen slope influenced by left-censored values.']

Plot for the default ('nan') method saved to: Examples/02_Censored_Seasonal_Trend/censored_seasonal_plot.png
```

### Why Do the Two Methods Give Such Different Results?

This example perfectly illustrates the impact of the `sens_slope_method` parameter.
-   **`nan` (Default)**: This method calculates the slope between all pairs of points where the result is unambiguous. Slopes between, for example, two left-censored points (`<35` and `<35`) are ambiguous and are ignored (treated as `NaN`). The final slope of `1.81` is the median of all the valid, unambiguous slopes. This result is close to the true slope of 2.0, as the level of censoring is not excessively high.
-   **`lwp` (Compatibility)**: This method handles ambiguous slopes by setting them to `0`. Because some of the data is censored, there are still ambiguous pairs. When these are replaced with `0`, they pull the median of all slopes downward, resulting in a lower estimated slope of `1.31`. This demonstrates how the `lwp` heuristic can bias the slope estimate towards zero, even with moderate censoring.

### What is `period=12`?

The `seasonal_trend_test` function requires a `period` argument to know how to group the data by season. For this example, the data has a repeating 12-month pattern. By setting `period=12`, we tell the function to deseasonalize the data by comparing January values to January values, February to February, and so on. This is the correct approach for monthly data. The previous use of `period=1` was incorrect as it would not perform any seasonal adjustment.

### Generated Plot

The plot visualizes the data and the trend calculated using the default (`nan`) method. Note how the censored data points (the red 'x's) are clustered during seasonal lows, consistent with the data generation process.

![Censored Seasonal Trend Plot](censored_seasonal_plot.png)
