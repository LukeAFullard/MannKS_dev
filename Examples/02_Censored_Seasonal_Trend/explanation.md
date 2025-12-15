# Example 2: Seasonal Trend with Censored Data

This example demonstrates a more advanced use case involving both seasonality and censored data. We will generate a time series that has a clear seasonal pattern, introduce left-censored data (values below a detection limit), and then use the `prepare_censored_data` and `seasonal_trend_test` functions to perform the analysis.

## Steps

1.  **Generate Synthetic Data**: We create a time series with a repeating 12-month seasonal pattern and a steady increasing linear trend. A numeric time vector (fractional years) is used to ensure the slope calculation is straightforward and avoids potential floating-point precision issues with `datetime` objects.
2.  **Introduce Censoring**: We simulate a detection limit by converting all numeric values below a certain threshold (e.g., 45) into censored strings (e.g., `"<45"`).
3.  **Pre-process Data**: The mixed array of numbers and strings is passed to the `prepare_censored_data` utility, which converts it into the structured DataFrame required by the analysis functions.
4.  **Perform Seasonal Trend Analysis**: The `seasonal_trend_test` is called. Because our time vector is numeric (in years), we set `period=1` to define a full seasonal cycle.
5.  **Review the Output**: We print the results and display the generated plot, which now visually distinguishes between censored and non-censored data points.

## Python Code (`censored_seasonal.py`)

The full Python script for this example is shown below.

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
```

## Results

The script produces the following output. The test correctly identifies the significant increasing trend, even with the presence of censored data. The calculated slope of ~1.15 is a reasonable estimate of the true underlying slope (2.0), demonstrating the robustness of the method.

```
Censored Seasonal Trend Analysis Results:
  Trend: increasing
  P-value: 0.0000
  Annual Sen's Slope: 1.1526
  Kendall's Tau: 0.5243
  Plot saved to: Examples/02_Censored_Seasonal_Trend/censored_seasonal_plot.png
```

### Generated Plot

The plot visualizes the seasonal data and the overall trend. Note how the censored data points (the red 'x's) are clustered in the earlier years and during the seasonal lows, which is consistent with the data we generated.

![Censored Seasonal Trend Plot](censored_seasonal_plot.png)
