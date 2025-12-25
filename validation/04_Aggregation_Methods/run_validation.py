import numpy as np
import pandas as pd
import os
import sys

# Add validation dir to path to import ValidationUtils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from validation_utils import ValidationUtils

def generate_tied_timestamp_data(n_months=24, trend_slope=0.0, noise_std=1.0, seed=42):
    np.random.seed(seed)

    dates = []
    values = []

    start_date = pd.Timestamp("2020-01-01")

    for i in range(n_months):
        # Base month start
        month_start = start_date + pd.DateOffset(months=i)

        # 3 to 5 observations per month
        n_obs = np.random.randint(3, 6)

        # Underlying trend value for this month
        base_value = 10 + i * trend_slope

        # Distribute observations within the month to avoid identical timestamps
        # and ensure deterministic selection by 'middle' aggregation.
        # We place one observation near the middle (Day 15) and others around it.
        # This removes ambiguity in tie-breaking when aggregating.
        days = np.linspace(1, 28, n_obs).astype(int)

        for d in days:
            dates.append(month_start + pd.Timedelta(days=d-1))
            # Add noise
            val = base_value + np.random.normal(0, noise_std)
            values.append(val)

    df = pd.DataFrame({'date': dates, 'value': values})
    return df

def run_validation():
    output_dir = os.path.dirname(__file__)
    utils = ValidationUtils(output_dir)

    # --- 1. Strong Increasing Trend (Generate Plot) ---
    df_inc = generate_tied_timestamp_data(n_months=36, trend_slope=0.5, noise_std=2.0, seed=101)

    res_inc, mk_result_inc = utils.run_comparison(
        test_id="V-04",
        df=df_inc,
        scenario_name="Strong_Increasing",
        true_slope=6.0, # 0.5 * 12
        lwp_mode_kwargs={
            'agg_method': 'lwp',
            'agg_period': 'month',
            'slope_scaling': 'year'
        },
        mk_kwargs={'slope_scaling': 'year'}
    )

    utils.generate_plot(df_inc, "V-04: Strong Increasing Trend (Standard MKS)", "01_strong_increasing_standard.png", mk_result=mk_result_inc)


    # --- 2. Weak Decreasing Trend (No Plot) ---
    df_dec = generate_tied_timestamp_data(n_months=36, trend_slope=-0.1, noise_std=2.0, seed=102)
    utils.run_comparison(
        test_id="V-04",
        df=df_dec,
        scenario_name="Weak_Decreasing",
        true_slope=-1.2,
        lwp_mode_kwargs={
            'agg_method': 'lwp',
            'agg_period': 'month',
            'slope_scaling': 'year'
        },
        mk_kwargs={'slope_scaling': 'year'}
    )

    # --- 3. Stable (No Trend) (No Plot) ---
    df_stable = generate_tied_timestamp_data(n_months=36, trend_slope=0.0, noise_std=2.0, seed=103)
    utils.run_comparison(
        test_id="V-04",
        df=df_stable,
        scenario_name="Stable",
        true_slope=0.0,
        lwp_mode_kwargs={
            'agg_method': 'lwp',
            'agg_period': 'month',
            'slope_scaling': 'year'
        },
        mk_kwargs={'slope_scaling': 'year'}
    )

    # --- Create Custom Report ---
    report_path = os.path.join(output_dir, 'README.md')
    with open(report_path, 'w') as f:
        f.write("# Validation Case V-04: Aggregation Methods\n\n")

        f.write("## Case Description\n")
        f.write("This validation case verifies the `agg_method` options for handling multiple observations per time period, "
                "specifically comparing the standard MannKenSen behavior against the LWP-TRENDS R script "
                "which enforces aggregation (e.g., one value per month). To ensure deterministic results, observations "
                "are distributed throughout the month, avoiding identical timestamps and ambiguous tie-breaking.\n\n")

        f.write("Three scenarios were tested:\n")
        f.write("1.  **Strong Increasing Trend:** A clear, statistically significant positive trend.\n")
        f.write("2.  **Weak Decreasing Trend:** A subtle, statistically significant (or borderline) negative trend.\n")
        f.write("3.  **Stable (No Trend):** Data with no underlying trend.\n\n")

        f.write("## Trend Figure (Strong Increasing)\n")
        f.write("The figure below shows the raw data (with multiple observations per month) and the standard Mann-Kendall Sen's slope trend line.\n\n")
        f.write("![Strong Increasing Trend](01_strong_increasing_standard.png)\n\n")

        f.write("## Results Table\n")
        if utils.results:
            long_rows = []
            for res in utils.results:
                test_id = res.get('test_id', 'Unknown')
                # Define method mappings
                methods = [
                    ('MannKenSen (Standard)', 'mk_py'),
                    ('MannKenSen (LWP Mode)', 'lwp_py'),
                    ('LWP-TRENDS (R)', 'r'),
                    ('MannKenSen (ATS)', 'ats_py'),
                    ('NADA2 (R)', 'nada_r')
                ]
                for method_name, prefix in methods:
                    row = {
                        'Test ID': test_id,
                        'Method': method_name,
                        'Slope': res.get(f'{prefix}_slope', np.nan),
                        'P-Value': res.get(f'{prefix}_p_value', np.nan),
                        'Lower CI': res.get(f'{prefix}_lower_ci', np.nan),
                        'Upper CI': res.get(f'{prefix}_upper_ci', np.nan)
                    }
                    long_rows.append(row)

            df_long = pd.DataFrame(long_rows)
            f.write(df_long.to_markdown(index=False))
            f.write("\n\n")

            f.write("## LWP Accuracy (Python vs R)\n")
            accuracy_rows = []
            for res in utils.results:
                accuracy_rows.append({
                    'Test ID': res.get('test_id'),
                    'Slope Error': res.get('slope_error'),
                    'Slope % Error': res.get('slope_pct_error')
                })
            df_acc = pd.DataFrame(accuracy_rows)
            f.write(df_acc.to_markdown(index=False))
            f.write("\n")

    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    run_validation()
