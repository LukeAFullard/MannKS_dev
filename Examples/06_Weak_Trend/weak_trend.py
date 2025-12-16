import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Base Synthetic Data
# Create a numeric time vector
n_points = 100
time_vector = np.arange(n_points)

# Generate a stable baseline with some noise
np.random.seed(42) # for reproducibility
intercept = 20
noise = np.random.normal(0, 5, n_points)
base_data = intercept + noise

# 2. Define a series of weak trends to test
# These slopes are small relative to the noise standard deviation (5)
# We will find a slope that produces a p-value between 0.1 and 0.4
# to demonstrate the "Likely Increasing" category.
weak_slopes = [0.0, 0.01, 0.015, 0.02, 0.03]
test_alpha = 0.4 # Use a high alpha to make "Likely" category reachable

print("--- Investigating the Effect of Trend Magnitude on Classification ---")
print(f"Using a custom significance level (alpha) of {test_alpha} to demonstrate 'Likely' trends.")
print("-" * 80)
print(f"{'True Slope':<12} | {'Estimated Slope':<18} | {'P-value':<10} | {'Significant?':<12} | {'Classification'}")
print("-" * 80)

final_data_values = None

# 3. Loop through each slope, add it to the data, and run the test
for i, slope in enumerate(weak_slopes):
    # Add the trend component to the base data
    trend_component = slope * time_vector
    data_values = base_data + trend_component

    # Keep the last dataset for the final plot
    if i == len(weak_slopes) - 1:
        final_data_values = data_values

    # Perform Trend Analysis with our custom alpha
    result = MannKenSen.trend_test(data_values, t=time_vector, alpha=test_alpha)

    # Print the key results in a formatted table
    print(f"{slope:<12.3f} | {result.slope:<18.4f} | {result.p:<10.4f} | {str(result.h):<12} | {result.classification}")

print("-" * 80)

# 4. Generate a plot for the final, strongest "weak" trend for visualization
if final_data_values is not None:
    # Rerun the test for the final slope to generate the plot
    MannKenSen.trend_test(
        final_data_values,
        t=time_vector,
        plot_path='Examples/06_Weak_Trend/weak_trend_plot.png'
    )
    print(f"\nA plot for the final trend (true slope={weak_slopes[-1]:.3f}) has been saved.")
