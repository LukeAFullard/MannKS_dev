
# Example 21: Seasonal Trend with Weekly Data

The `MannKenSen` package is not limited to monthly or annual seasons. It can perform seasonal trend analysis on any regular time interval by specifying the `season_type` and `period`.

This example demonstrates an analysis of weekly data, testing for an overall trend while accounting for variations between each day of the week.

## 1. Data Generation

We generate 5 years of weekly data with two patterns:
1.  A steady long-term **decreasing** trend.
2.  A weekly seasonal pattern where values are slightly lower on weekends (Saturday and Sunday).

```python
import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Synthetic Data
np.random.seed(42)
n_years = 5
t = pd.to_datetime(pd.date_range(start='2018-01-01', periods=n_years * 52, freq='W'))

# Create a long-term decreasing trend
long_term_trend = np.linspace(10, 0, len(t))

# Create a weekly seasonal pattern (lower on weekends)
seasonal_pattern = np.array([-0.5 if day in [5, 6] else 0.5 for day in t.dayofweek])

# Combine with noise
noise = np.random.normal(0, 0.5, len(t))
x = long_term_trend + seasonal_pattern + noise

# 2. Run the Seasonal Trend Test
# For 'day_of_week', the period is 7
plot_path = 'seasonal_weekly_trend.png'
result = MannKenSen.seasonal_trend_test(x, t, season_type='day_of_week', period=7, plot_path=plot_path)

print(result)
```

## 2. Results

The `seasonal_trend_test` function returns a single `namedtuple` object that summarizes the overall trend across all seasons. The test combines the evidence from each day of the week to produce one set of statistics.

```
trend: decreasing\nh: True\np: 0.0000\nz: -21.5982\nclassification: Highly Likely Decreasing\nslope: -1.9817 (units/year)
```

The result shows a **'Highly Likely Decreasing'** trend with a very small p-value. The function correctly identified the strong, underlying decreasing trend present in the data, even with the weekly seasonal pattern.

## 3. Plot

The generated plot is the primary tool for visualizing the behavior of individual seasons. Each subplot shows the data for a specific day of the week (Monday=0, Sunday=6). The plot visually confirms that a decreasing trend is present for every day, consistent with the overall result.

![Seasonal Weekly Trend Plot](seasonal_weekly_trend.png)
