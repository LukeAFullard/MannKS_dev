# MannKenSen

This project provides a Python implementation of the Mann-Kendall test for trend analysis. The original code was sourced from the `pyMannKendall` package and has been modified to support unequally spaced time series data. The `pyMannKendall` code will be deleted once we are production ready.

## MannKenSen Package

The `MannKenSen` package is a new addition to this project that provides modified versions of the Mann-Kendall test and Sen's slope estimator to handle unequally spaced time series data.

### `original_test(x, t, alpha=0.05)`

This function performs the Mann-Kendall test on unequally spaced time series data.

**Input:**
- `x`: A vector of data.
- `t`: A vector of timestamps corresponding to the data. The function automatically handles numeric vectors, as well as `numpy.datetime64` and Python `datetime` objects by converting them to Unix timestamps.
- `alpha`: The significance level (default is 0.05).

**Output:**
A named tuple with the following fields:
- `trend`: The trend of the data ('increasing', 'decreasing', or 'no trend').
- `h`: A boolean indicating whether the trend is significant.
- `p`: The p-value of the test.
- `z`: The Z-statistic.
- `Tau`: Kendall's Tau.
- `s`: The Mann-Kendall score.
- `var_s`: The variance of `s`.
- `slope`: The Sen's slope.
- `intercept`: The intercept of the trend line.
- `lower_ci`: The lower confidence interval of the slope.
- `upper_ci`: The upper confidence interval of the slope.
- `C`: The confidence of the trend direction.
- `Cd`: The confidence that the trend is decreasing.


### `seasonal_test(x, t, period=12, alpha=0.05, agg_method='none', season_type='month')`

This function performs the seasonal Mann-Kendall test on unequally spaced time series data.

**Input:**
- `x`: A vector of data.
- `t`: A vector of timestamps. Can be a numeric vector or a datetime-like array (e.g., `numpy.datetime64` or a list of Python `datetime` objects).
- `period`: The seasonal period. For numeric `t`, this defines the cycle length (e.g., 12 for monthly data if `t` is in months). For datetime `t`, this must match the expected period of the `season_type`.
- `alpha`: The significance level (default is 0.05).
- `agg_method`: The method for aggregating multiple data points within the same season-year.
  - `'none'` (default): Performs the analysis on all individual data points.
  - `'median'`: Aggregates data using the median of the values and times.
  - `'middle'`: Aggregates data by selecting the observation closest to the middle of the time period.
- `season_type`: For datetime inputs, specifies how to define a season. See the table below for options.

**Output:**
A named tuple with the same fields as `original_test`.

#### `season_type` Options for Datetime Inputs

| `season_type`    | Description                               | Expected `period` |
|------------------|-------------------------------------------|-------------------|
| `'month'`        | Month of the year (1-12)                  | 12                |
| `'day_of_week'`  | Day of the week (0=Mon, 6=Sun)            | 7                 |
| `'quarter'`      | Quarter of the year (1-4)                 | 4                 |
| `'hour'`         | Hour of the day (0-23)                    | 24                |
| `'week_of_year'` | ISO week of the year (1-53)               | 52 or 53          |
| `'day_of_year'`  | Day of the year (1-366)                   | (no validation)   |
| `'minute'`       | Minute of the hour (0-59)                 | 60                |
| `'second'`       | Second of the minute (0-59)               | 60                |

**Example: Weekly Seasonality**
```python
import numpy as np
import pandas as pd
from MannKenSen import seasonal_test

# Create 4 years of weekly data
t = pd.to_datetime(pd.date_range(start='2020-01-01', periods=208, freq='W'))
x = np.random.rand(208)

# Inject a clear increasing trend in the 10th week of each year
tenth_week_mask = t.isocalendar().week == 10
x[tenth_week_mask] = [10, 20, 30, 40]

# Perform the test for weekly seasonality
result = seasonal_test(x, t, period=53, season_type='week_of_year')
print(result)
```
