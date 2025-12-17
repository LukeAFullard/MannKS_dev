import numpy as np
import pandas as pd
import MannKenSen
import os

def main():
    """
    Generate a dataset to test the 'HiCensor' rule and compare MannKenSen's
    implementation with the LWP-TRENDS R script.
    """
    # 1. Generate Synthetic Data
    # A dataset with a clear trend and multiple censoring levels is needed to
    # demonstrate the HiCensor rule effectively.
    np.random.seed(123)
    time_vector = np.arange(2000, 2020)
    slope = 0.5
    intercept = 5
    noise = np.random.normal(0, 2, len(time_vector))
    data_values = intercept + slope * (time_vector - time_vector[0]) + noise

    # Introduce multiple censoring levels
    censored_data = data_values.copy().astype(object)
    censored_data[data_values < 4] = '<4'
    censored_data[data_values < 2] = '<2'

    output_dir = "validation/09_HiCensor_Rule"
    os.makedirs(output_dir, exist_ok=True)

    # 2. Save for R Validation
    df_raw = MannKenSen.prepare_censored_data(censored_data)
    df_to_save = pd.DataFrame({
        'Year': time_vector,
        'Value': censored_data,
        'Censored': df_raw['censored'],
        'CenType': df_raw['cen_type']
    })
    csv_path = os.path.join(output_dir, "validation_data_hicensor.csv")
    df_to_save.to_csv(csv_path, index=False)

    # 3. Run MannKenSen Analysis
    prepared_data = MannKenSen.prepare_censored_data(censored_data)

    print("--- MannKenSen 'HiCensor' Rule Validation ---")

    # --- Analysis without HiCensor rule ---
    print("\n--- Analysis with HiCensor=False (Default) ---")
    plot_path_default = os.path.join(output_dir, "manken_plot_default.png")
    result_default = MannKenSen.trend_test(
        x=prepared_data,
        t=time_vector,
        hicensor=False, # Explicitly false for clarity
        plot_path=plot_path_default
    )
    print(f"{'Method':<12} | {'P-value':<10} | {'Z-stat':<10} | {'Slope':<10} | {'90% CI'}")
    print("-" * 65)
    ci_default = f"[{result_default.lower_ci:.3f}, {result_default.upper_ci:.3f}]"
    print(f"{'Default':<12} | {result_default.p:<10.4f} | {result_default.z:<10.4f} | {result_default.slope:<10.4f} | {ci_default}")

    # --- Analysis with HiCensor rule ---
    print("\n--- Analysis with HiCensor=True ---")
    plot_path_hicensor = os.path.join(output_dir, "manken_plot_hicensor.png")
    result_hicensor = MannKenSen.trend_test(
        x=prepared_data,
        t=time_vector,
        hicensor=True,
        plot_path=plot_path_hicensor
    )
    print(f"{'Method':<12} | {'P-value':<10} | {'Z-stat':<10} | {'Slope':<10} | {'90% CI'}")
    print("-" * 65)
    ci_hicensor = f"[{result_hicensor.lower_ci:.3f}, {result_hicensor.upper_ci:.3f}]"
    print(f"{'HiCensor':<12} | {result_hicensor.p:<10.4f} | {result_hicensor.z:<10.4f} | {result_hicensor.slope:<10.4f} | {ci_hicensor}")

    print("\n" + "="*65)
    print("Validation data and plots saved to:", output_dir)
    print("="*65)

if __name__ == "__main__":
    main()
