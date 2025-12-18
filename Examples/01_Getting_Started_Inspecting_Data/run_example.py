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
