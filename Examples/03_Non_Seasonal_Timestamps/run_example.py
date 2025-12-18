import numpy as np
import pandas as pd
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# This example introduces the use of a datetime object for the time vector,
# which is the most common use case for real-world time series data.
np.random.seed(42)
n_samples = 120 # 10 years of monthly data
dates = pd.date_range(start='2010-01-01', periods=n_samples, freq='MS')

# Create a slight downward trend of ~0.5 units per year and add noise
time_as_years = np.arange(n_samples) / 12.0
trend = -0.5 * time_as_years
noise = np.random.normal(0, 0.8, n_samples)
values = 10 + trend + noise

# --- 2. Perform the Trend Test with Plotting ---
# The trend_test function automatically converts datetime objects to numeric
# timestamps for the calculation.
# We also use the `plot_path` argument to save a visualization of the results.
result = mks.trend_test(
    x=values,
    t=dates,
    plot_path='Examples/03_Non_Seasonal_Timestamps/timestamp_trend_plot.png'
)

# --- 3. Print Key Results ---
# --- 3. Print Key Results ---
# When using datetime objects, the raw slope is calculated in units per second
# (Unix time). To make it human-readable, we convert it to units per year.
SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
annual_slope = result.slope * SECONDS_PER_YEAR
median_val = np.median(values)
annual_percent_change = (annual_slope / median_val) * 100

print("--- MannKenSen Trend Analysis Results (with Timestamps) ---")
print(f"Trend Classification: {result.classification}")
print(f"P-value (p): {result.p:.4f}")
print(f"Annual Sen's Slope: {annual_slope:.4f} (units per year)")
print(f"Annual Percent Change: {annual_percent_change:.2f}%")
