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

# --- 3. Format Results and Generate README ---
# When using datetime objects, the raw slope is calculated in units per second
# (Unix time). To make it human-readable, we convert it to units per year.
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
annual_slope = result.slope * SECONDS_PER_YEAR
median_val = np.median(values)
annual_percent_change = (annual_slope / median_val) * 100

result_summary = f"""
- **Trend Classification:** {result.classification}
- **P-value (p):** {result.p:.4f}
- **Annual Sen's Slope:** {annual_slope:.4f} (units per year)
- **Annual Percent Change:** {annual_percent_change:.2f}%
"""

readme_content = f"""
# Example 3: Non-Seasonal Trend Test with Timestamps

This example demonstrates how to perform a trend test on a time series that uses `datetime` objects for its time vector, which is the most common format for real-world data. It also shows how to generate and interpret a trend plot.

## Script: `run_example.py`
The script performs the following actions:
1.  Generates 10 years of synthetic monthly data with a slight downward trend.
2.  Calls `mks.trend_test`, passing the `pandas.DatetimeIndex` as the time vector `t`.
3.  Uses the `plot_path` argument to save a visualization of the trend analysis.
4.  Converts the raw Sen's slope (which is in units/second) to a more interpretable annual slope.
5.  Dynamically generates this `README.md` file, embedding the captured results and the plot.

## Results
The key results from the analysis are summarized below.

{result_summary}

### Plot Interpretation (`timestamp_trend_plot.png`)
The generated plot provides a comprehensive visual summary of the analysis:
-   **Data Points:** The raw data points are plotted over time.
-   **Sen's Slope Line:** The solid red line shows the calculated Sen's slope, representing the main trend line.
-   **Confidence Intervals:** The dashed red lines show the 95% confidence intervals for the slope. A narrower interval indicates higher confidence in the slope estimate.

![Trend Plot](timestamp_trend_plot.png)

**Conclusion:** The `MannKenSen` package seamlessly handles `datetime` objects, making it easy to analyze real-world time series data. The plotting feature is a crucial tool for visualizing and communicating the results of the trend analysis.
"""

with open('Examples/03_Non_Seasonal_Timestamps/README.md', 'w') as f:
    f.write(readme_content)

print("Successfully generated README and plot for Example 3.")
