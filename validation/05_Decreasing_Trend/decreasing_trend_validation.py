import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Synthetic Data
# Create a time vector of years. This is a simpler format that LWP-TRENDS can handle reliably.
years = np.arange(2000, 2090)

# Define a decreasing trend
true_slope = -0.5
intercept = 50
trend_component = true_slope * np.arange(len(years))

# Add some random noise to make it more realistic
np.random.seed(42)  # for reproducibility
noise = np.random.normal(0, 5, len(years))

# Combine components to create the final data series
data_values = intercept + trend_component + noise

# 2. Save Data for R Validation
# Create a DataFrame with just Year and Value, and save to CSV.
df = pd.DataFrame({'Year': years, 'Value': data_values})
df.to_csv('validation/05_Decreasing_Trend/validation_data.csv', index=False)


# 3. Perform Trend Analysis with MannKenSen
# The plot_path will save the trend plot to a file.
# We use the 'years' vector as the time input.
result = MannKenSen.trend_test(
    data_values,
    t=years,
    plot_path='validation/05_Decreasing_Trend/decreasing_trend_plot.png'
)

# 4. Print the Results
# The output will clearly show a significant decreasing trend.
print("--- MannKenSen Analysis Results ---")
print(f"  Classification: {result.classification}")
print(f"  Trend Exists: {result.h}")
print(f"  P-value: {result.p:.4f}")
print(f"  Sen's Slope: {result.slope:.4f}")
print(f"  Confidence Interval: {result.lower_ci:.4f} to {result.upper_ci:.4f}")
