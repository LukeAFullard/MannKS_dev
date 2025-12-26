import os
import sys
import numpy as np
import pandas as pd
import MannKenSen as mk
from typing import Dict, Tuple

# Add parent directory to path to import ValidationUtils
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from validation_utils import ValidationUtils

class ValidationUtilsV7(ValidationUtils):
    def run_comparison_v7(self, test_id: str, df: pd.DataFrame, scenario_name: str, true_slope: float = None) -> Tuple[Dict, object]:
        full_test_id = f"{test_id}_{scenario_name}"
        print(f"Running comparison for: {full_test_id}")

        # --- Python Standard (Scaled) ---
        # We pass the datetime objects directly to verify scaling logic inside trend_test
        # slope_scaling='year' converts from per-second to per-year
        mk_std_scaled = mk.trend_test(df['value'], df['date'], slope_scaling='year')

        # --- Python LWP Mode (Scaled) ---
        lwp_defaults = {
            'mk_test_method': 'lwp',
            'ci_method': 'lwp',
            'sens_slope_method': 'lwp',
            'agg_method': 'middle_lwp'
        }
        mk_lwp_scaled = mk.trend_test(df['value'], df['date'], slope_scaling='year', **lwp_defaults)

        # --- Python ATS ---
        mk_ats = mk.trend_test(df['value'], df['date'], sens_slope_method='ats', slope_scaling='year')

        # --- R LWP Script ---
        r_res = self.run_lwp_r_script(df)

        # --- R NADA2 Script ---
        nada_res = self.run_nada2_r_script(df)

        slope_error = np.nan
        slope_pct_error = np.nan

        if not np.isnan(r_res['slope']):
            slope_error = mk_lwp_scaled.slope - r_res['slope']

            if true_slope is not None and true_slope != 0:
                slope_pct_error = (slope_error / true_slope) * 100
            elif r_res['slope'] != 0:
                slope_pct_error = (slope_error / r_res['slope']) * 100
            elif slope_error == 0:
                slope_pct_error = 0.0

        result_row = {
            'test_id': full_test_id,
            'mk_py_slope': mk_std_scaled.slope,
            'mk_py_p_value': mk_std_scaled.p,
            'mk_py_lower_ci': mk_std_scaled.lower_ci,
            'mk_py_upper_ci': mk_std_scaled.upper_ci,
            'lwp_py_slope': mk_lwp_scaled.slope,
            'lwp_py_p_value': mk_lwp_scaled.p,
            'lwp_py_lower_ci': mk_lwp_scaled.lower_ci,
            'lwp_py_upper_ci': mk_lwp_scaled.upper_ci,
            'r_slope': r_res['slope'],
            'r_p_value': r_res['p_value'],
            'r_lower_ci': r_res['lower_ci'],
            'r_upper_ci': r_res['upper_ci'],
            'ats_py_slope': mk_ats.slope,
            'ats_py_p_value': mk_ats.p,
            'ats_py_lower_ci': mk_ats.lower_ci,
            'ats_py_upper_ci': mk_ats.upper_ci,
            'nada_r_slope': nada_res['slope'],
            'nada_r_p_value': nada_res['p_value'],
            'nada_r_lower_ci': nada_res['lower_ci'],
            'nada_r_upper_ci': nada_res['upper_ci'],
            'slope_error': slope_error,
            'slope_pct_error': slope_pct_error
        }

        self.results.append(result_row)
        self._append_to_csv(result_row)
        return result_row, mk_std_scaled

def run_validation():
    output_dir = os.path.dirname(__file__)
    utils = ValidationUtilsV7(output_dir)
    scenarios = []

    # --- Scenario 1: Strong Increasing Trend ---
    np.random.seed(42)
    dates = pd.date_range(start='2010-01-01', end='2019-12-01', freq='MS') # 10 years
    n = len(dates)
    slope_annual = 2.0
    slope_monthly = slope_annual / 12
    noise = np.random.normal(0, 0.5, n)
    values = slope_monthly * np.arange(n) + 10 + noise
    df_strong = pd.DataFrame({'date': dates, 'value': values})

    _, mk_res_strong = utils.run_comparison_v7('V-07', df_strong, 'strong_increasing', true_slope=slope_annual)
    scenarios.append({
        'df': df_strong,
        'title': 'Strong Increasing (Scaled)',
        'mk_result': mk_res_strong
    })

    # --- Scenario 2: Weak Decreasing Trend ---
    slope_annual_weak = -0.5
    slope_monthly_weak = slope_annual_weak / 12
    noise_weak = np.random.normal(0, 1.5, n)
    values_weak = slope_monthly_weak * np.arange(n) + 20 + noise_weak
    df_weak = pd.DataFrame({'date': dates, 'value': values_weak})

    _, mk_res_weak = utils.run_comparison_v7('V-07', df_weak, 'weak_decreasing', true_slope=slope_annual_weak)
    scenarios.append({
        'df': df_weak,
        'title': 'Weak Decreasing (Scaled)',
        'mk_result': mk_res_weak
    })

    # --- Scenario 3: Stable (No Trend) ---
    slope_annual_stable = 0.0
    noise_stable = np.random.normal(0, 1.0, n)
    values_stable = 15 + noise_stable
    df_stable = pd.DataFrame({'date': dates, 'value': values_stable})

    _, mk_res_stable = utils.run_comparison_v7('V-07', df_stable, 'stable', true_slope=0.0)
    scenarios.append({
        'df': df_stable,
        'title': 'Stable (Scaled)',
        'mk_result': mk_res_stable
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v07_combined.png", "V-07: Slope Scaling Analysis")

    # Create final report
    utils.create_report()

if __name__ == "__main__":
    run_validation()
