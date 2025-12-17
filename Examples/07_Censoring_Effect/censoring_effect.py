import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Base Synthetic Data with a Known Trend
n_points = 100
time_vector = np.arange(n_points)
true_slope = 0.25
intercept = 10
np.random.seed(42)  # for reproducibility
noise = np.random.normal(0, 4, n_points)
data_values = intercept + true_slope * time_vector + noise

# 2. Define Censoring Proportions to Test
censor_proportions = [0.0, 0.20, 0.40, 0.60]

print("--- Investigating the Effect of Censoring on Trend Estimation ---")
print("-" * 80)
print(f"{'Censor %':<10} | {'True Slope':<12} | {'Estimated Slope':<18} | {'Confidence Interval'}")
print("-" * 80)

# 3. Loop through each proportion, apply censoring, and run the test
for prop in censor_proportions:
    # Create a fresh copy of the data for censoring
    censored_data_mixed = data_values.copy()

    if prop > 0:
        # Determine a censoring threshold (e.g., the 40th percentile of the data).
        # This ensures that the points we choose to censor are realistically low values.
        censor_threshold = np.percentile(data_values, 40)

        # Find all indices that are candidates for censoring (i.e., below the threshold).
        candidate_indices = np.where(data_values < censor_threshold)[0]

        # Calculate the total number of points to censor based on the desired proportion
        # of the *entire* dataset.
        n_to_censor = int(n_points * prop)

        # We can only censor as many points as are available below our threshold.
        # This prevents an error if we ask for 60% censoring but only 40% of points
        # are below the threshold.
        n_to_censor = min(n_to_censor, len(candidate_indices))

        # Randomly choose the indices to censor from the candidates.
        censor_indices = np.random.choice(candidate_indices, size=n_to_censor, replace=False)

        # Convert numeric values to left-censored strings
        censored_data_mixed = censored_data_mixed.astype(object)
        censored_data_mixed[censor_indices] = f'<{censor_threshold:.2f}'

    # Use the preprocessing function to handle the mixed data types
    prepared_data = MannKenSen.prepare_censored_data(censored_data_mixed)

    # Define a unique plot path for each proportion
    plot_filename = f"Examples/07_Censoring_Effect/censoring_effect_{int(prop*100)}pct.png"

    # Perform the trend test on the prepared (potentially censored) data
    result = MannKenSen.trend_test(
        x=prepared_data,
        t=time_vector,
        plot_path=plot_filename
    )

    # Print the comparative results
    ci_str = f"[{result.lower_ci:.4f}, {result.upper_ci:.4f}]"
    print(f"{prop*100:<9.1f}% | {true_slope:<12.3f} | {result.slope:<18.4f} | {ci_str}")

print("-" * 80)
print("\nPlots for each censoring level have been saved.")
