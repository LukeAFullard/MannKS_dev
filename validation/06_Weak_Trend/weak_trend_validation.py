import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Synthetic Data
# Create a time vector of years for LWP-TRENDS compatibility.
years = np.arange(2000, 2100)
n_points = len(years)

# Generate a stable baseline with some noise
np.random.seed(42)  # for reproducibility
intercept = 20
noise = np.random.normal(0, 5, n_points)
base_data = intercept + noise

# Define a weak but persistent increasing trend
weak_slope = 0.03
trend_component = weak_slope * np.arange(n_points)
data_values = base_data + trend_component

# 2. Save Data for R Validation
# Create a DataFrame with Year and Value and save to CSV.
df = pd.DataFrame({'Year': years, 'Value': data_values})
df.to_csv('validation/06_Weak_Trend/validation_data.csv', index=False)

# 3. Perform Trend Analysis with MannKenSen
# We use a custom alpha to demonstrate the 'Likely Increasing' category.
test_alpha = 0.4
result = MannKenSen.trend_test(
    data_values,
    t=years,
    alpha=test_alpha,
    plot_path='validation/06_Weak_Trend/weak_trend_plot.png'
)

# 4. Print the Results
print("--- MannKenSen Analysis Results ---")
print(f"  Classification: {result.classification}")
print(f"  Trend Exists (at alpha={test_alpha}): {result.h}")
print(f"  P-value: {result.p:.4f}")
print(f"  Sen's Slope: {result.slope:.4f}")
print(f"  Confidence Interval: {result.lower_ci:.4f} to {result.upper_ci:.4f}")
