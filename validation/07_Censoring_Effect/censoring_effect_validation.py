import numpy as np
import pandas as pd
import MannKenSen
import os

def main():
    """
    Generate synthetic data with varying levels of censoring, run trend analysis
    using the default 'robust' method, and save the data for R validation.
    """
    # 1. Generate Base Synthetic Data with a Known Trend
    n_points = 100
    time_vector = np.arange(n_points)
    true_slope = 0.25
    intercept = 10
    np.random.seed(42)  # for reproducibility
    noise = np.random.normal(0, 4, n_points)
    data_values = intercept + true_slope * time_vector + noise

    # Define output directory
    output_dir = "validation/07_Censoring_Effect"
    os.makedirs(output_dir, exist_ok=True)

    # 2. Define Censoring Proportions to Test
    censor_proportions = [0.0, 0.20, 0.40, 0.60]

    print("--- Effect of Censoring on Trend Estimation (MannKenSen Robust Method) ---")

    # 3. Loop through each proportion, apply censoring, and run the test
    for prop in censor_proportions:
        # Create a fresh copy of the data for censoring
        censored_data_mixed = data_values.copy()
        censor_threshold_val = np.percentile(data_values, 40)
        censored_col = [False] * n_points
        cen_type_col = ['not'] * n_points

        if prop > 0:
            candidate_indices = np.where(data_values < censor_threshold_val)[0]
            n_to_censor = int(n_points * prop)
            n_to_censor = min(n_to_censor, len(candidate_indices))
            censor_indices = np.random.choice(candidate_indices, size=n_to_censor, replace=False)

            # Convert numeric values to left-censored strings for processing
            censored_data_mixed = censored_data_mixed.astype(object)
            censored_data_mixed[censor_indices] = f'<{censor_threshold_val:.2f}'
            for i in censor_indices:
                censored_col[i] = True
                cen_type_col[i] = 'left'


        # Save the data for R validation
        df = pd.DataFrame({
            'time': time_vector,
            'original_value': data_values,
            'value_for_manken': censored_data_mixed,
            'Censored': censored_col,
            'CenType': cen_type_col
        })
        csv_path = os.path.join(output_dir, f"validation_data_{int(prop*100)}pct.csv")
        df.to_csv(csv_path, index=False)

        # Use the preprocessing function to handle the mixed data types
        prepared_data = MannKenSen.prepare_censored_data(censored_data_mixed)

        # --- Perform Trend Analysis ---
        plot_path = os.path.join(output_dir, f"manken_plot_{int(prop*100)}pct.png")
        result = MannKenSen.trend_test(
            x=prepared_data,
            t=time_vector,
            plot_path=plot_path
        )

        # --- Print the comparative results ---
        print(f"\n--- Censoring Level: {prop*100:.0f}% ---")
        print(f"{'Method':<12} | {'P-value':<10} | {'Z-stat':<10} | {'Slope':<10} | {'90% CI'}")
        print("-" * 65)
        ci_str = f"[{result.lower_ci:.3f}, {result.upper_ci:.3f}]"
        print(f"{'Robust':<12} | {result.p:<10.4f} | {result.z:<10.4f} | {result.slope:<10.4f} | {ci_str}")

    print("\n" + "="*65)
    print("Validation data and plots saved to:", output_dir)
    print("="*65)

if __name__ == "__main__":
    main()
