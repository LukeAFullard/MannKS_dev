import numpy as np
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# This example demonstrates the simplest use case: a non-seasonal trend test
# on a dataset with a simple numeric time vector.
np.random.seed(42)
n_samples = 50
time = np.arange(n_samples)

# Create data with a clear upward trend (slope of approx. 0.1) and add noise
trend = 0.1 * time
noise = np.random.normal(0, 0.5, n_samples)
values = trend + noise

# --- 2. Perform the Trend Test ---
# Call the trend_test function with the data.
# Since the data is not censored, we don't need to pre-process it.
result = mks.trend_test(x=values, t=time)

# --- 3. Print and Interpret the Results ---
print("--- MannKenSen Trend Analysis Results ---")
print(f"Trend Classification: {result.classification}")
print(f"Is Trend Significant? (h): {result.h}")
print(f"P-value (p): {result.p:.4f}")
print(f"Sen's Slope: {result.slope:.4f}")
print(f"Intercept: {result.intercept:.4f}")
print(f"95% Confidence Intervals: [{result.lower_ci:.4f}, {result.upper_ci:.4f}]")
print(f"Mann-Kendall Score (s): {result.s}")
print(f"Kendall's Tau: {result.Tau:.4f}")
