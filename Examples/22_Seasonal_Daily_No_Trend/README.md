
# Example 22: Seasonal Trend with Daily Data (No Trend)

A key capability of the seasonal trend test is to distinguish between a true long-term trend and strong, regular seasonality. A dataset can have a very prominent seasonal pattern but no actual year-over-year trend.

This example demonstrates how the test correctly identifies "No Trend" in such a scenario.

## 1. Data Generation

We generate 4 years of daily data. The data has a strong sinusoidal pattern, simulating high values in the summer and low values in the winter. Crucially, **no long-term trend** is added; the data is stationary.

```python
import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Synthetic Data
np.random.seed(1)
n_years = 4
t = pd.to_datetime(pd.date_range(start='2020-01-01', periods=n_years * 365, freq='D'))

# Create a strong seasonal pattern (sine wave over the year)
seasonal_cycle = 10 * np.sin(2 * np.pi * t.dayofyear / 365.25)

# Add noise, but NO long-term trend
noise = np.random.normal(0, 2.0, len(t))
x = seasonal_cycle + noise

# 2. Run the Seasonal Trend Test
# We test for trends within each month, so period is 12
plot_path = 'seasonal_daily_no_trend.png'
result = MannKenSen.seasonal_trend_test(x, t, season_type='month', period=12, plot_path=plot_path)

print(result)
```

## 2. Results

The test analyzes the trend *within* each season. For example, it compares the data from January 2020, January 2021, January 2022, and so on. Because there is no year-over-year trend in any month, the combined result correctly shows no overall trend.

```
trend: no trend\nh: False\np: 0.8636\nz: -0.1717\nclassification: No Trend
```

The high p-value and "No Trend" classification confirm that the test was not fooled by the strong seasonal pattern.

## 3. Plot

The plot clearly visualizes the situation. The main plot (top left) shows the strong yearly cycle. However, each of the seasonal subplots (for each month) shows a nearly horizontal trend line, confirming the absence of a long-term trend within any given month.

![Seasonal Daily No Trend Plot](seasonal_daily_no_trend.png)
