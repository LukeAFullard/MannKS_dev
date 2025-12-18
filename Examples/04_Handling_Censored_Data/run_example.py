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

# --- 4. Format Results and Generate README ---
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
annual_slope = result.slope * SECONDS_PER_YEAR
median_val = np.median(prepared_data['value'])
annual_percent_change = (annual_slope / median_val) * 100

result_summary = f"""
- **Trend Classification:** {result.classification}
- **P-value (p):** {result.p:.4f}
- **Annual Sen's Slope:** {annual_slope:.4f} (units per year)
- **Proportion of Data Censored:** {result.prop_censored:.2%}
"""

readme_content = f"""
# Example 4: Handling Basic Censored Data

This example demonstrates the essential workflow for handling time series data that contains censored values (e.g., values reported as below or above a laboratory detection limit, such as `"<5"` or `">50"`).

## Key Concepts

The statistical methods in `MannKenSen` are specifically designed to handle censored data correctly. However, you must pre-process your data before running the trend test. This is a deliberate design choice to ensure the user is aware of the data conversion process.

The workflow is a two-step process:
1.  **`mks.prepare_censored_data(x)`:** This function takes your raw, mixed-type data (numbers and strings) and returns a `pandas.DataFrame` with three columns: `value` (the numeric limit), `censored` (boolean), and `cen_type` (`'lt'` for left-censored, `'gt'` for right-censored, or `'not'` for uncensored).
2.  **`mks.trend_test(x, t)`:** You then pass this **prepared DataFrame** as the `x` argument to the trend test function. The function will automatically detect the special format and apply the appropriate censored-data statistics.

## Script: `run_example.py`
The script generates a synthetic quarterly dataset with an upward trend. It then introduces both left-censored (`<`) and right-censored (`>`) values. It follows the two-step workflow described above and saves a plot of the results. Finally, it dynamically generates this README file.

## Results
The key results from the analysis are summarized below.

{result_summary}

### Plot Interpretation (`censored_trend_plot.png`)
The plot provides a clear visualization of the censored data:
-   **Uncensored Data:** Plotted as solid blue circles.
-   **Left-Censored Data (`<`):** Plotted as green triangles pointing downwards.
-   **Right-Censored Data (`>`):** Plotted as green triangles pointing upwards.

This allows for a quick and intuitive assessment of how the censored data is distributed within the time series.

![Censored Trend Plot](censored_trend_plot.png)

**Conclusion:** Handling censored data is a core feature of the `MannKenSen` package. By using the simple `prepare_censored_data` -> `trend_test` workflow, you can perform a statistically robust trend analysis on complex, real-world datasets.
"""

with open('Examples/04_Handling_Censored_Data/README.md', 'w') as f:
    f.write(readme_content)

print("Successfully generated README and plot for Example 4.")
