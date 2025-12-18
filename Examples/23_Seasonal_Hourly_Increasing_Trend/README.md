
# Example 23: Seasonal Trend with Hourly Data

The seasonal trend test can be applied to high-frequency data, such as hourly measurements, to identify long-term trends while accounting for daily (diurnal) cycles.

This example demonstrates how to configure the test for hourly data with a 24-hour seasonal period.

## The Python Script

The following script generates 4 weeks of hourly data with two key patterns:
1.  A steady long-term **increasing** trend.
2.  A strong **diurnal cycle**, simulating a repeating 24-hour pattern.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# 1. Generate Synthetic Data
np.random.seed(1)
n_weeks = 4
t = pd.to_datetime(pd.date_range(start='2023-01-01', periods=n_weeks * 7 * 24, freq='h'))

# Create a long-term increasing trend
long_term_trend = np.linspace(0, 15, len(t))

# Create a strong diurnal (daily) pattern
diurnal_cycle = 5 * np.sin(2 * np.pi * t.hour / 24)

# Combine with noise
noise = np.random.normal(0, 1.5, len(t))
x = long_term_trend + diurnal_cycle + noise

# 2. Run the Seasonal Trend Test
plot_path = 'seasonal_hourly_trend.png'
# For a daily cycle in hourly data, season_type='hour' and period=24
result = mks.seasonal_trend_test(x, t, season_type='hour', period=24, plot_path=plot_path)

# 3. Print the result
print(result)

```

## Command Output

Running the script produces a single result object that summarizes the overall trend across all seasons (hours of the day).

```
Seasonal_Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(0.0), z=np.float64(30.024066860011953), Tau=np.float64(0.8207671957671958), s=np.float64(7446.0), var_s=np.float64(61488.0), slope=np.float64(6.165636718695981e-06), intercept=np.float64(-10312.022502970387), lower_ci=np.float64(5.981785368995765e-06), upper_ci=np.float64(6.337188398828679e-06), C=1.0, Cd=0.0, classification='Highly Likely Increasing', analysis_notes=[], sen_probability=np.float64(2.6278183966225263e-198), sen_probability_max=np.float64(2.6278183966225263e-198), sen_probability_min=np.float64(2.6278183966225263e-198), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0)
```

## Interpretation of Results

The test is configured with `season_type='hour'` and `period=24`. It analyzes the trend for each hour of the day across the 4-week period. For example, it compares the data from 01:00 on day 1, 01:00 on day 2, and so on.

The combined result is a **'Highly Likely Increasing'** classification, with a very small p-value. This shows that the test successfully detected the underlying increasing trend amidst the strong daily cycle.

## Plot

The plot shows the data for all 24 seasons (hours). While the diurnal cycle is visible in the main plot (top left), each individual hourly subplot clearly shows the long-term increasing trend, consistent with the overall result.

![Seasonal Hourly Trend Plot](seasonal_hourly_trend.png)
