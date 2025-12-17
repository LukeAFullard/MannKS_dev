import numpy as np
import pandas as pd
import MannKenSen
import os

def main():
    """
    Generate datasets with right-censored and mixed-censored data,
    run trend analysis, and save data for R validation.
    """
    # 1. Define Base Data Parameters
    n_points = 100
    time_vector = np.arange(n_points)
    true_slope = 0.25
    intercept = 10
    np.random.seed(42)
    noise = np.random.normal(0, 4, n_points)
    data_values = intercept + true_slope * time_vector + noise

    output_dir = "validation/08_Right_Censored_Data"
    os.makedirs(output_dir, exist_ok=True)

    # 2. Scenarios to test
    scenarios = {
        "right_censored": {"right_prop": 0.3, "left_prop": 0.0},
        "mixed_censored": {"right_prop": 0.2, "left_prop": 0.2},
    }

    for name, props in scenarios.items():
        print(f"\n--- Scenario: {name.replace('_', ' ').title()} ---")

        # --- Generate Censored Data ---
        censored_data = data_values.copy().astype(object)

        # Right censoring
        if props["right_prop"] > 0:
            threshold = np.percentile(data_values, 100 - (props["right_prop"] * 100))
            indices = np.where(data_values > threshold)[0]
            censored_data[indices] = f'>{threshold:.2f}'

        # Left censoring
        if props["left_prop"] > 0:
            threshold = np.percentile(data_values, props["left_prop"] * 100)
            indices = np.where(data_values < threshold)[0]
            censored_data[indices] = f'<{threshold:.2f}'

        # --- Save for R Validation ---
        df_raw = MannKenSen.prepare_censored_data(censored_data)
        df_to_save = pd.DataFrame({
            'time': time_vector,
            'value_for_manken': censored_data,
            'Censored': df_raw['censored'],
            'CenType': df_raw['cen_type']
        })
        csv_path = os.path.join(output_dir, f"validation_data_{name}.csv")
        df_to_save.to_csv(csv_path, index=False)

        # --- Run MannKenSen Analysis ---
        prepared_data = MannKenSen.prepare_censored_data(censored_data)
        plot_path = os.path.join(output_dir, f"manken_plot_{name}.png")
        result = MannKenSen.trend_test(
            x=prepared_data,
            t=time_vector,
            plot_path=plot_path
        )

        # --- Print Results ---
        print(f"{'Method':<12} | {'P-value':<10} | {'Z-stat':<10} | {'Slope':<10} | {'90% CI'}")
        print("-" * 65)
        ci_str = f"[{result.lower_ci:.3f}, {result.upper_ci:.3f}]"
        print(f"{'Robust':<12} | {result.p:<10.4f} | {result.z:<10.4f} | {result.slope:<10.4f} | {ci_str}")

    print("\n" + "="*65)
    print("Validation data and plots saved to:", output_dir)
    print("="*65)

if __name__ == "__main__":
    main()
