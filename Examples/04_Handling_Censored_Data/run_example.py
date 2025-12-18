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
