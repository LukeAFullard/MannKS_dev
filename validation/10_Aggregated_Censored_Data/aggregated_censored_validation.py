import numpy as np
import pandas as pd
import MannKenSen
import os

def main():
    """
    Generate a censored dataset with multiple observations per time period,
    run an aggregated trend analysis, and save data for R validation.
    """
    # 1. Generate Synthetic Data
    np.random.seed(456)
    years = np.repeat(np.arange(2000, 2020), 4) # 4 observations per year
    time_vector = years + np.tile([0.1, 0.4, 0.6, 0.9], 20)
    slope = 0.3
    intercept = 8
    noise = np.random.normal(0, 3, len(time_vector))
    data_values = intercept + slope * (time_vector - time_vector.min()) + noise

    # Introduce censoring
    censored_data = data_values.copy().astype(object)
    censored_data[data_values < 7] = '<7'

    output_dir = "validation/10_Aggregated_Censored_Data"
    os.makedirs(output_dir, exist_ok=True)

    # 2. Save for R Validation
    df_raw = MannKenSen.prepare_censored_data(censored_data)
    df_to_save = pd.DataFrame({
        'Year': years,
        'Value': censored_data,
        'Censored': df_raw['censored'],
        'CenType': df_raw['cen_type']
    })
    csv_path = os.path.join(output_dir, "validation_data_aggregated.csv")
    df_to_save.to_csv(csv_path, index=False)

    # 3. Run MannKenSen Analysis with Aggregation
    prepared_data = MannKenSen.prepare_censored_data(censored_data)

    print("--- MannKenSen Aggregated Censored Data Validation ---")
    plot_path = os.path.join(output_dir, "manken_plot_aggregated.png")

    # Corrected call to trend_test
    # The `t` parameter should be the years for aggregation
    result = MannKenSen.trend_test(
        x=prepared_data,
        t=years,
        agg_method='median', # Aggregate data before analysis
        plot_path=plot_path
    )

    print(f"{'Method':<25} | {'P-value':<10} | {'Z-stat':<10} | {'Slope':<10} | {'90% CI'}")
    print("-" * 75)
    ci_str = f"[{result.lower_ci:.3f}, {result.upper_ci:.3f}]"
    print(f"{'MannKenSen (Aggregated)':<25} | {result.p:<10.4f} | {result.z:<10.4f} | {result.slope:<10.4f} | {ci_str}")

    print("\n" + "="*75)
    print("Validation data and plots saved to:", output_dir)
    print("="*75)

if __name__ == "__main__":
    main()
