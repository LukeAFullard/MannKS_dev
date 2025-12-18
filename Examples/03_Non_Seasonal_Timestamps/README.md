
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


- **Trend Classification:** Highly Likely Decreasing
- **P-value (p):** 0.0000
- **Annual Sen's Slope:** -0.4814 (units per year)
- **Annual Percent Change:** -6.42%


### Plot Interpretation (`timestamp_trend_plot.png`)
The generated plot provides a comprehensive visual summary of the analysis:
-   **Data Points:** The raw data points are plotted over time.
-   **Sen's Slope Line:** The solid red line shows the calculated Sen's slope, representing the main trend line.
-   **Confidence Intervals:** The dashed red lines show the 95% confidence intervals for the slope. A narrower interval indicates higher confidence in the slope estimate.

![Trend Plot](timestamp_trend_plot.png)

**Conclusion:** The `MannKenSen` package seamlessly handles `datetime` objects, making it easy to analyze real-world time series data. The plotting feature is a crucial tool for visualizing and communicating the results of the trend analysis.
