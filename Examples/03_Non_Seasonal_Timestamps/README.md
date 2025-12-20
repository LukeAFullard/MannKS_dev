
# Example 3: Non-Seasonal Trend Test with Timestamps

This example demonstrates how to perform a trend test on a time series that uses `datetime` objects and how to use the automatic slope scaling feature.

## The Python Script

The script generates 10 years of synthetic monthly data with a slight downward trend. It then calls `mks.trend_test`, passing a `pandas.DatetimeIndex` as the time vector `t`. Crucially, it also uses two new parameters:
-   `x_unit="mg/L"`: Specifies the units of the data.
-   `slope_scaling="year"`: Instructs the function to automatically scale the Sen's slope to "units per year".

```python

import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# 1. Generate Synthetic Data
np.random.seed(42)
n_samples = 120 # 10 years of monthly data
dates = pd.date_range(start='2010-01-01', periods=n_samples, freq='MS')

# Create a slight downward trend of ~0.5 units per year
time_as_years = np.arange(n_samples) / 12.0
trend = -0.5 * time_as_years
noise = np.random.normal(0, 0.8, n_samples)
values = 10 + trend + noise

# 2. Perform the Trend Test with Plotting and Slope Scaling
plot_path = 'timestamp_trend_plot.png'
result = mks.trend_test(
    x=values,
    t=dates,
    plot_path=plot_path,
    x_unit="mg/L",
    slope_scaling="year"
)

# 3. Print the full result
print(result)

```

## Command Output

Running the script prints the full result object.

```
Mann_Kendall_Test(trend='decreasing', h=np.True_, p=np.float64(0.0), z=np.float64(-11.484101811164521), Tau=np.float64(-0.7092436974789915), s=np.float64(-5064.0), var_s=np.float64(194366.66666666666), slope=np.float64(-0.48143203596202394), intercept=np.float64(29.137930460405457), lower_ci=np.float64(-1.6673206534219808e-08), upper_ci=np.float64(-1.3763644045328411e-08), C=1.0, Cd=1.0, classification='Highly Likely Decreasing', analysis_notes=[], sen_probability=np.float64(1.0), sen_probability_max=np.float64(1.0), sen_probability_min=np.float64(1.0), prop_censored=np.float64(0.0), prop_unique=1.0, n_censor_levels=0, slope_per_second=np.float64(-1.5255660632051358e-08), scaled_slope=np.float64(-0.48143203596202394), slope_units='mg/L per year')
```

## Interpretation of Results

*   **Automatic Slope Scaling:** Because we set `slope_scaling="year"`, the `slope` field in the result is now automatically presented in **units per year**. The calculated slope of approximately -0.5 is consistent with the trend we built into the data.
*   **New Output Fields:**
    *   `slope`: This now contains the user-friendly scaled slope.
    *   `slope_units`: This field clearly states the units of the slope, e.g., `'mg/L per year'`.
    *   `slope_per_second`: The raw, unscaled slope in units per second is still available for users who need it.
*   **Significance:** The very low p-value and significant result (`h=True`) confirm that a statistically significant downward trend was detected.

### Plot Interpretation (`timestamp_trend_plot.png`)
The generated plot is also updated with the new information:
-   The statistics box now displays the scaled slope along with its new, descriptive units, making the plot much easier to interpret at a glance.

![Trend Plot](timestamp_trend_plot.png)

**Conclusion:** The new `x_unit` and `slope_scaling` parameters make it much easier to get an interpretable Sen's slope when working with `datetime` objects, removing the need for manual conversion.
