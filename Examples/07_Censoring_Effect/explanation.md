# Example 07: Effect of Censoring on Trend Analysis

This example demonstrates how different proportions of censored data can impact the results of a trend analysis, particularly the estimated Sen's slope and its confidence interval.

## Process

1.  **Generate Data**: We create a synthetic dataset with a known, strong increasing trend (`true_slope = 0.25`).
2.  **Iterate on Censoring**: We loop through a list of censoring proportions (0%, 20%, 40%, 60%).
3.  **Apply Left-Censoring**: In each loop, we apply left-censoring to the data. To do this realistically, we first set a `censor_threshold` at the 40th percentile of the data. We then randomly select a percentage of the *total* data points from the pool of values that fall below this threshold and replace them with a censored string (e.g., `"<15.23"`).
4.  **Pre-process Data**: We use the `MannKenSen.prepare_censored_data` utility function to convert our mixed-type array (numbers and strings) into a format suitable for the trend test.
5.  **Run Test and Compare**: We run the `trend_test` for each censoring level and print the results in a comparative table. We focus on how the estimated slope and the width of the confidence interval change as more data becomes censored.
6.  **Save Plots**: A separate plot is saved for each scenario to provide a clear visual comparison.

## Python Script (`censoring_effect.py`)

```python
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
```

## Results

The output table shows a clear pattern:
- With **0% censoring**, the estimated slope is very close to the true slope, and the confidence interval is narrow.
- With **20% censoring**, the slope estimate remains accurate, but the confidence interval widens slightly, reflecting the increased uncertainty.
- At **40% censoring**, the slope estimate starts to deviate, and the confidence interval becomes much wider. The test has less information to work with.
- The results for **60% censoring** are identical to 40%. This is because our censoring threshold was the 40th percentile, so a maximum of 40% of the data points were eligible for censoring. This demonstrates a realistic constraint in highly censored datasets.

```
--- Investigating the Effect of Censoring on Trend Estimation ---
--------------------------------------------------------------------------------
Censor %   | True Slope   | Estimated Slope    | Confidence Interval
--------------------------------------------------------------------------------
0.0      % | 0.250        | 0.2565             | [0.2327, 0.2830]
20.0     % | 0.250        | 0.2563             | [0.2121, 0.2993]
40.0     % | 0.250        | 0.1962             | [0.0856, 0.2949]
60.0     % | 0.250        | 0.1962             | [0.0856, 0.2949]
--------------------------------------------------------------------------------

Plots for each censoring level have been saved.
```

## Plots

Four plots were generated, one for each scenario. Here is the plot for the 40% censored case, where the censored data points are shown in a different color.

![Censoring Effect Plot (40%)](censoring_effect_40pct.png)
