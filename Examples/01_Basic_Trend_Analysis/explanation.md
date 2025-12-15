# Example 1: Basic Trend Analysis

This example demonstrates the most common use case for the `MannKenSen` package: performing a standard, non-seasonal trend analysis. We will use the `trend_test` function to analyze a synthetic time series.

## Steps

1.  **Generate Synthetic Data**: We create a simple linear time series with a known slope and add some random noise to make it more realistic. For clarity, the time vector `t` is a simple NumPy array representing years.
2.  **Perform Trend Analysis**: We call the `trend_test` function, passing in our data (`x`) and time (`t`) vectors. We also provide a `plot_path` to save a visualization of the results.
3.  **Review the Output**: We print the key results from the analysis and display the generated plot.

## Python Code (`basic_trend.py`)

The full Python script for this example is shown below.

```python
import numpy as np
from MannKenSen import trend_test

def main():
    """
    Generate a simple linear time series with noise and perform a trend analysis.
    """
    # 1. Generate Synthetic Data
    # Create a time series of 20 years of annual data
    t = np.arange(2000, 2020, dtype=float)

    # Generate a linear trend with a known slope and some random noise
    slope = 2.5 # The slope is in units per year
    intercept = 10
    noise = np.random.normal(0, 5, len(t))
    x = slope * (t - t[0]) + intercept + noise

    # 2. Perform Trend Analysis
    # The plot_path will save the visualization to a file
    plot_path = "Examples/01_Basic_Trend_Analysis/basic_trend_plot.png"
    result = trend_test(x, t, plot_path=plot_path)

    # 3. Print the Results
    # Since the time vector `t` is in years, the resulting slope is already an annual slope.
    print("Basic Trend Analysis Results:")
    print(f"  Trend: {result.trend}")
    print(f"  P-value: {result.p:.4f}")
    print(f"  Annual Sen's Slope: {result.slope:.4f}")
    print(f"  Kendall's Tau: {result.Tau:.4f}")
    print(f"  Plot saved to: {plot_path}")

if __name__ == "__main__":
    main()
```

## Results

Running the script produces the following output. The test correctly identifies a significant (`p < 0.0001`) increasing trend. The calculated Annual Sen's Slope of ~2.8 is a robust estimate of the true slope we defined (2.5), and the high Kendall's Tau value indicates a strong positive correlation.

```
Basic Trend Analysis Results:
  Trend: increasing
  P-value: 0.0000
  Annual Sen's Slope: 2.7944
  Kendall's Tau: 0.8632
  Plot saved to: Examples/01_Basic_Trend_Analysis/basic_trend_plot.png
```

### Generated Plot

The plot saved by the script provides a clear visualization of the data, the calculated Sen's slope trend line, and the 95% confidence intervals.

![Basic Trend Analysis Plot](basic_trend_plot.png)
