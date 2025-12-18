# Example 4: Handling Basic Censored Data

### Goal

This example demonstrates the essential workflow for handling time series data that contains **censored values** (e.g., values reported as below or above a detection limit, like `'<5'` or `'>50'`). Correctly processing this data is crucial for an accurate trend analysis.

The key takeaway is the mandatory pre-processing step using the `MannKenSen.prepare_censored_data()` function.

### Python Script (`run_example.py`)

The script below generates a synthetic dataset with quarterly samples over 20 years. The data has a clear upward trend and includes several left-censored (`<`) and right-censored (`>`) values.

```python
import numpy as np
import pandas as pd
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# This example demonstrates the essential workflow for handling censored data.
np.random.seed(42)
n_samples = 80
dates = pd.date_range(start='2015-01-01', periods=n_samples, freq='QS-OCT')

# Create data with an upward trend and some noise
time_as_years = np.arange(n_samples) / 4.0 # Quarterly data
trend = 0.3 * time_as_years
noise = np.random.normal(0, 0.7, n_samples)
values = (5 + trend + noise).astype(object)

# Introduce some left-censored ('<') and right-censored ('>') values
values[10] = '<2.5'
values[25] = '<3.0'
values[40] = '<3.0'
values[60] = '>12.0'
values[70] = '>12.0'

# --- 2. Pre-process the Censored Data ---
# Before running the trend test, the raw data must be processed using the
# `prepare_censored_data` function. This function takes your raw data
# (which can be a mix of numbers and strings) and converts it into a
# uniform format that the trend testing functions can understand.
# It returns a DataFrame with 'value', 'censored', and 'cen_type' columns.
prepared_data = mks.prepare_censored_data(x=values)

# --- 3. Perform the Trend Test with Plotting ---
# The trend_test is then called on this prepared DataFrame. The package
# automatically detects the censored data columns and applies the correct
# statistical methods.
result = mks.trend_test(
    x=prepared_data,
    t=dates,
    plot_path='Examples/04_Handling_Censored_Data/censored_trend_plot.png'
)

# --- 4. Print Key Results ---
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
annual_slope = result.slope * SECONDS_PER_YEAR
median_val = np.median(prepared_data['value'])
annual_percent_change = (annual_slope / median_val) * 100

print("--- MannKenSen Trend Analysis Results (Censored Data) ---")
print(f"Trend Classification: {result.classification}")
print(f"P-value (p): {result.p:.4f}")
print(f"Annual Sen's Slope: {annual_slope:.4f} (units per year)")
print(f"Annual Percent Change: {annual_percent_change:.2f}%")
print(f"Proportion of Data Censored: {result.prop_censored:.2%}")

```

### Results and Interpretation

Running the script produces the following output and plot:

```
--- MannKenSen Trend Analysis Results (Censored Data) ---
Trend Classification: Highly Likely Increasing
P-value (p): 0.0000
Annual Sen's Slope: 0.3112 (units per year)
Annual Percent Change: 3.96%
Proportion of Data Censored: 6.25%
```

![Censored Trend Plot](censored_trend_plot.png)

#### Interpretation:

-   **The `prepare_censored_data` Step:** This is the most important part of the workflow. The `trend_test` function cannot directly accept string values like `'<5'`. The `prepare_censored_data` function correctly parses these strings, separating them into a numeric `value` (the detection limit), a boolean `censored` flag, and a `cen_type` ('lt' or 'gt'). The trend test is then performed on this structured data.
-   **Statistical Results:** The analysis found a `Highly Likely Increasing` trend with a statistically significant `p-value` of `0.0000`. The calculated `Annual Sen's Slope` of `0.3112` is very close to our true synthetic slope of 0.3, demonstrating that the test accurately handled the censored values and captured the underlying trend.
-   **Plot Visualization:** The plot clearly distinguishes between the non-censored data points (black circles) and the censored ones (red triangles). This is crucial for visually assessing the potential influence of censored data. Here, we see a few censored points at the beginning and end of the series, but they follow the overall pattern and do not appear to be driving the trend. The robust statistical methods used by `MannKenSen` ensure they are handled appropriately in the calculation.
