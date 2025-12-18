import numpy as np
import pandas as pd
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# Create a synthetic dataset representing monthly water quality samples
# over 5 years.
np.random.seed(42)
n_samples = 60
dates = pd.date_range(start='2018-01-01', periods=n_samples, freq='MS')

# Create a slight upward trend and add some noise
trend = np.linspace(5, 8, n_samples)
noise = np.random.normal(0, 1.5, n_samples)
values = (trend + noise).astype(object)

# Introduce some missing data by replacing some values with NaN
values[10:15] = np.nan
values[40] = np.nan

# Introduce some left-censored data
values[5] = '<2.0'
values[25] = '<2.5'
values[50] = '<2.0'

# --- 2. Run the Inspection ---
# The inspect_trend_data function is the best first step in any analysis.
# It provides a high-level overview of the data's structure, completeness,
# and censoring patterns.

# First, prepare the raw data to handle censored values. This creates the
# 'censored' and 'cen_type' columns required for plotting.
prepared_data = mks.prepare_censored_data(values)
df = pd.DataFrame({
    'date': dates,
    'value': prepared_data['value'],
    'censored': prepared_data['censored'],
    'cen_type': prepared_data['cen_type']
})


# The `plot=True` argument generates a 2x2 grid of plots that are
# essential for visual diagnosis. `plot_path` saves the figure.
# We capture the printed output to embed it in the README.
import io
from contextlib import redirect_stdout

f = io.StringIO()
with redirect_stdout(f):
    mks.inspect_trend_data(
        df,
        value_col='value',
        time_col='date',
        plot=True,
        plot_path='Examples/01_Getting_Started_Inspecting_Data/inspection_plots.png'
    )
inspection_output = f.getvalue()


# --- 3. Generate README ---
readme_content = f"""
# Example 1: Getting Started - Inspecting Your Data

The first and most important step in any trend analysis is to thoroughly inspect your data. The `MannKenSen.inspect_trend_data` function is designed for this purpose. It provides a quick statistical and visual overview of your time series, helping you identify potential issues like missing data, censored values, and irregular sampling.

## Script: `run_example.py`
The script performs the following actions:
1.  Generates a synthetic 5-year monthly dataset with an upward trend.
2.  Intentionally introduces missing data (`NaN`) and left-censored (`<`) values to simulate a real-world dataset.
3.  Calls `mks.prepare_censored_data` to process the raw data.
4.  Calls `mks.inspect_trend_data` with `plot=True` to generate a summary and a set of diagnostic plots.
5.  Dynamically generates this `README.md` file, embedding the captured output below.

## Results

### Statistical Summary
The `inspect_trend_data` function prints a high-level summary of the dataset's properties. This includes the time range, number of records, percentage of missing and censored data, and the number of unique censoring levels.

```text
{inspection_output}
```

### Visual Inspection (`inspection_plots.png`)
The function also generates a 2x2 grid of plots for a quick visual diagnosis:
-   **Time Series Plot:** Shows the data over time, with censored values marked.
-   **Value Matrix:** A heatmap showing the distribution of values by year and month.
-   **Censoring Matrix:** A heatmap indicating where censored data occurs.
-   **Sample Count Matrix:** A heatmap showing the number of samples per period, which is useful for identifying irregular sampling.

![Inspection Plots](inspection_plots.png)

**Conclusion:** Before performing any trend tests, always inspect your data. This initial step can reveal critical issues that might otherwise lead to incorrect or misleading trend results.
"""

with open('Examples/01_Getting_Started_Inspecting_Data/README.md', 'w') as f:
    f.write(readme_content)

print("Successfully generated README and plots for Example 1.")
