# Example 3: Non-Seasonal Trend Test with Timestamps

### Goal

This example demonstrates the most common real-world use case for `MannKenSen`: analyzing a time series where the time component is represented by `datetime` objects. It also introduces the `plot_path` parameter to automatically generate and save a visualization of the trend analysis.

### Python Script (`run_example.py`)

The script below generates a synthetic dataset representing 10 years of monthly data with a slight downward trend. The time vector is created using `pandas.date_range`. The script then calls `MannKenSen.trend_test()` to perform the analysis and saves a plot of the results.

A crucial part of this example is the **interpretation of the slope**. When `datetime` objects are used, the package converts them to high-resolution numeric timestamps (Unix time in seconds) for the calculation. This results in a raw slope in **units per second**, which is a very small number. To make it human-readable, we must convert it to **units per year** by multiplying by the number of seconds in a year.

```python
import numpy as np
import pandas as pd
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# This example introduces the use of a datetime object for the time vector,
# which is the most common use case for real-world time series data.
np.random.seed(42)
n_samples = 120 # 10 years of monthly data
dates = pd.date_range(start='2010-01-01', periods=n_samples, freq='MS')

# Create a slight downward trend of ~0.5 units per year and add noise
time_as_years = np.arange(n_samples) / 12.0
trend = -0.5 * time_as_years
noise = np.random.normal(0, 0.8, n_samples)
values = 10 + trend + noise

# --- 2. Perform the Trend Test with Plotting ---
# The trend_test function automatically converts datetime objects to numeric
# timestamps for the calculation.
# We also use the `plot_path` argument to save a visualization of the results.
result = mks.trend_test(
    x=values,
    t=dates,
    plot_path='Examples/03_Non_Seasonal_Timestamps/timestamp_trend_plot.png'
)

# --- 3. Print Key Results ---
# When using datetime objects, the raw slope is calculated in units per second
# (Unix time). To make it human-readable, we convert it to units per year.
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
annual_slope = result.slope * SECONDS_PER_YEAR
median_val = np.median(values)
annual_percent_change = (annual_slope / median_val) * 100

print("--- MannKenSen Trend Analysis Results (with Timestamps) ---")
print(f"Trend Classification: {result.classification}")
print(f"P-value (p): {result.p:.4f}")
print(f"Annual Sen's Slope: {annual_slope:.4f} (units per year)")
print(f"Annual Percent Change: {annual_percent_change:.2f}%")

```

### Results and Interpretation

Running the script produces the following output and plot:

```
--- MannKenSen Trend Analysis Results (with Timestamps) ---
Trend Classification: Highly Likely Decreasing
P-value (p): 0.0000
Annual Sen's Slope: -0.4814 (units per year)
Annual Percent Change: -6.42%
```

![Trend Plot](timestamp_trend_plot.png)

#### Interpretation:

-   **Annual Sen's Slope:** After converting from units/second, the calculated annual slope is `-0.4814` units per year. This is very close to the true synthetic slope of -0.5, confirming the test's accuracy. The negative value indicates a decreasing trend.
-   **Trend Classification:** The `Highly Likely Decreasing` classification and `p-value` of `0.0000` show that the detected downward trend is statistically significant.
-   **Plot Visualization:** The generated plot provides a clear visual confirmation of the analysis.
    -   The black dots represent the individual monthly data points.
    -   The solid blue line is the Sen's slope trend line, clearly showing the downward trajectory.
    -   The dashed blue lines represent the 95% confidence intervals for the slope. The fact that this confidence band is narrow and does not cross the horizontal (zero-slope) plane gives us high confidence in the trend.
    -   The key statistics are conveniently printed on the plot itself, making it a self-contained summary of the analysis.
