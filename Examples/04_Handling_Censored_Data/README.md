
# Example 4: Handling Basic Censored Data

This example demonstrates the essential workflow for handling time series data that contains censored values (e.g., values reported as below or above a laboratory detection limit, such as `"<5"` or `">50"`).

## Key Concepts

The statistical methods in `MannKenSen` are designed to handle censored data correctly. However, you must first pre-process your data. This is a deliberate design choice to ensure you are aware of the data conversion process.

The workflow is a two-step process:
1.  **`mks.prepare_censored_data(x)`:** This function takes your raw, mixed-type data and returns a `pandas.DataFrame` with three columns: `value` (the numeric limit), `censored` (boolean), and `cen_type` (`'lt'` for left-censored, `'gt'` for right-censored, or `'not'` for uncensored).
2.  **`mks.trend_test(x, t)`:** You then pass this **prepared DataFrame** as the `x` argument to the trend test function. The function will automatically detect this special format and apply the appropriate censored-data statistics.

## The Python Script

The script below generates a synthetic quarterly dataset with an upward trend, introduces both left-censored (`<`) and right-censored (`>`) values, and then follows the two-step workflow.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# 1. Generate Synthetic Data
np.random.seed(42)
n_samples = 80
dates = pd.date_range(start='2015-01-01', periods=n_samples, freq='QS-OCT')

# Create data with an upward trend
time_as_years = np.arange(n_samples) / 4.0
trend = 0.3 * time_as_years
noise = np.random.normal(0, 0.7, n_samples)
values = (5 + trend + noise)

# Introduce censored values as strings
values_str = [f"{v:.2f}" for v in values]
values_str[10] = '<2.5'
values_str[25] = '<3.0'
values_str[40] = '<3.0'
values_str[60] = '>12.0'
values_str[70] = '>12.0'

# 2. Pre-process the Censored Data
print("--- Prepared Data (first 5 rows) ---")
prepared_data = mks.prepare_censored_data(x=values_str)
print(prepared_data.head())

# 3. Perform the Trend Test
print("\n--- Trend Test Result ---")
plot_path = 'censored_trend_plot.png'
result = mks.trend_test(x=prepared_data, t=dates, plot_path=plot_path)
print(result)

```

## Command Output

Running the script first prints the head of the `prepared_data` DataFrame, showing how the raw strings have been converted. It then prints the final trend test result.

```
--- Prepared Data (first 5 rows) ---
   value  censored cen_type
0   5.35     False      not
1   4.98     False      not
2   5.60     False      not
3   6.29     False      not
4   5.14     False      not

--- Trend Test Result ---
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(0.0), z=np.float64(9.265236389550891), Tau=np.float64(0.7241036567326997), s=np.float64(2228.0), var_s=np.float64(57773.333333333336), slope=np.float64(9.864113715055603e-09), intercept=np.float64(-9.221835654890256), lower_ci=np.float64(8.786158421194918e-09), upper_ci=np.float64(1.0922353531842581e-08), C=1.0, Cd=0.0, classification='Highly Likely Increasing', analysis_notes=['WARNING: Sen slope influenced by right-censored values.'], sen_probability=np.float64(2.7711285746302167e-20), sen_probability_max=np.float64(2.7711285746302167e-20), sen_probability_min=np.float64(2.7711285746302167e-20), prop_censored=np.float64(0.0625), prop_unique=0.925, n_censor_levels=3)
```

## Interpretation of Results

*   **Data Preparation:** The first part of the output shows the structured DataFrame created by `prepare_censored_data`. Notice how `'<2.5'` is converted into a row with `value=2.5`, `censored=True`, and `cen_type='lt'`.
*   **Trend Result:** Despite some of the data being censored, the test correctly identifies the underlying **'Highly Likely Increasing'** trend with a very small p-value. The `prop_censored` field in the result confirms that `6.25%` of the data was censored.

### Plot Interpretation (`censored_trend_plot.png`)
The plot provides a clear visualization of the censored data:
-   **Uncensored Data:** Plotted as solid blue circles.
-   **Left-Censored Data (`<`):** Plotted as green triangles pointing downwards.
-   **Right-Censored Data (`>`):** Plotted as green triangles pointing upwards.

![Censored Trend Plot](censored_trend_plot.png)

**Conclusion:** Handling censored data is a core feature of the `MannKenSen` package. By using the simple `prepare_censored_data` -> `trend_test` workflow, you can perform a statistically robust trend analysis on complex, real-world datasets.
