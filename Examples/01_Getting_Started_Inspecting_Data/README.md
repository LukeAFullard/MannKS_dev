# Example 1: Getting Started - Inspecting Your Data

### Goal

This example demonstrates the crucial first step in any trend analysis workflow: **inspecting your data**. Before running any statistical tests, it's essential to understand the structure, completeness, and quality of your time series.

The `MannKenSen` package provides the `inspect_trend_data()` function for this purpose. This example shows how to use it to generate a set of diagnostic plots that provide a high-level overview of the data.

### Python Script (`run_example.py`)

The following script generates a synthetic dataset representing a typical environmental monitoring scenario, with monthly samples over five years, some missing data, and a few censored data points. It then runs the inspection function to generate the diagnostic plots.

```python
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
mks.inspect_trend_data(
    df,
    value_col='value',
    time_col='date',
    plot=True,
    plot_path='Examples/01_Getting_Started_Inspecting_Data/inspection_plots.png'
)

print("Successfully generated inspection plots for Example 1.")

```

### Results and Interpretation

Running the script generates the following 2x2 grid of diagnostic plots:

![Inspection Plots](inspection_plots.png)

Here is how to interpret each plot:

1.  **Time Series Plot (Top Left):**
    -   **What it shows:** This is a standard time series plot of the data values over time. Censored data points are highlighted in red.
    -   **Interpretation:** This plot provides an initial visual sense of any potential trend. In this case, we can see a slight upward movement over the five-year period. The red dots immediately draw attention to the presence and location of censored data.

2.  **Value Matrix (Top Right):**
    -   **What it shows:** This is a heatmap where each cell represents a month (x-axis) and a year (y-axis). The color of the cell corresponds to the data value.
    -   **Interpretation:** This view is excellent for spotting seasonal patterns and outliers. A strong seasonal pattern would appear as consistent vertical bands of color (e.g., all summers being red/hot). Here, the colors gradually shift from lighter to darker vertically, reinforcing the presence of a long-term trend rather than a seasonal cycle. White cells indicate months with no data.

3.  **Censoring Matrix (Bottom Left):**
    -   **What it shows:** This heatmap highlights which observations are censored. Blue cells are non-censored, red cells are censored, and white cells are missing.
    -   **Interpretation:** This plot is crucial for diagnosing issues with censored data. It helps you see if censoring is consistent or if it changes over time. For example, if all the red cells were at the beginning of the period, it might indicate that the lab's detection limit improved over time, which is a key consideration for trend analysis. Here, the censoring is sporadic, which is less of a concern.

4.  **Sample Count Matrix (Bottom Right):**
    -   **What it shows:** This heatmap shows the number of samples recorded in each month/year cell.
    -   **Interpretation:** This is a powerful tool for understanding data completeness and sampling frequency. In this ideal example, most cells have a value of 1. The white cells clearly show the data gap between late 2018 and early 2019, which was synthetically introduced. This visual confirmation of data gaps is essential for determining if the dataset is suitable for seasonal or non-seasonal analysis.

By using this single function, a user can quickly gain a deep understanding of their dataset's characteristics before committing to a full statistical analysis.
