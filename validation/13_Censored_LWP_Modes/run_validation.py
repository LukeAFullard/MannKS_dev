import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from validation.validation_utils import ValidationUtils
import MannKenSen as mk
import matplotlib.pyplot as plt

def generate_censored_data(n=24, slope=1.0, noise_std=0.5, start_year=2000, censor_pct=0.3):
    """
    Generates monthly data with a linear trend and right-censoring.
    """
    # Create monthly dates
    dates = []
    current_date = datetime(start_year, 1, 15) # Mid-month
    for i in range(n):
        dates.append(current_date)
        # Advance one month
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 15)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 15)

    t = np.arange(n)
    noise = np.random.normal(0, noise_std, n)
    base_values = slope * t + 10 + noise

    # Apply Right Censoring
    threshold = np.percentile(base_values, (1 - censor_pct) * 100)

    final_values = []
    cen_type = []

    for v in base_values:
        if v > threshold:
            final_values.append(f">{threshold:.1f}")
            cen_type.append('gt')
        else:
            final_values.append(v)
            cen_type.append('not')

    return pd.DataFrame({'date': dates, 'value': final_values, 'cen_type': cen_type})

def run():
    # Use the specific output directory
    output_dir = os.path.join(repo_root, 'validation', '13_Censored_LWP_Modes')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    utils = ValidationUtils(output_dir)
    scenarios = []

    # Define LWP kwargs for this specific validation case
    lwp_kwargs = {
        'mk_test_method': 'lwp',
        'ci_method': 'lwp',
        'sens_slope_method': 'lwp',
        'lt_mult': 0.5,
        'gt_mult': 1.1,
    }

    # Scenario 1: Strong Increasing Trend (Right Censored)
    print("Generating Scenario 1: Strong Increasing")
    df_strong = generate_censored_data(n=48, slope=2.0, noise_std=1.0, censor_pct=0.3)

    _, mk_std_strong = utils.run_comparison(
        test_id="V-13",
        df=df_strong,
        scenario_name="strong_increasing",
        lwp_mode_kwargs=lwp_kwargs,
        true_slope=2.0
    )
    scenarios.append({
        'df': df_strong,
        'title': 'Strong Increasing (Right Censored)',
        'mk_result': mk_std_strong
    })

    # Scenario 2: Weak Decreasing Trend
    print("Generating Scenario 2: Weak Decreasing")
    df_weak = generate_censored_data(n=48, slope=-0.2, noise_std=1.0, censor_pct=0.3)
    _, mk_std_weak = utils.run_comparison(
        test_id="V-13",
        df=df_weak,
        scenario_name="weak_decreasing",
        lwp_mode_kwargs=lwp_kwargs,
        true_slope=-0.2
    )
    scenarios.append({
        'df': df_weak,
        'title': 'Weak Decreasing (Right Censored)',
        'mk_result': mk_std_weak
    })

    # Scenario 3: Stable (No Trend)
    print("Generating Scenario 3: Stable")
    df_stable = generate_censored_data(n=48, slope=0.0, noise_std=1.0, censor_pct=0.3)
    _, mk_std_stable = utils.run_comparison(
        test_id="V-13",
        df=df_stable,
        scenario_name="stable",
        lwp_mode_kwargs=lwp_kwargs,
        true_slope=0.0
    )
    scenarios.append({
        'df': df_stable,
        'title': 'Stable (Right Censored)',
        'mk_result': mk_std_stable
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v13_combined.png", "V-13: LWP Censored Compatibility Analysis")

    # Generate Report
    description = """
# Validation Case V-13: Censored LWP Compatibility Modes

This validation case focuses on verifying the "LWP Compatibility Mode" of the `mannkensen` package against the original LWP-TRENDS R script, specifically for **right-censored** data.

The goal is to demonstrate that setting parameters `mk_test_method='lwp'` and `sens_slope_method='lwp'` allows Python to accurately replicate the R script's handling of censored values.

## Methodology
- **Data:** 4 years of monthly data (n=48).
- **Censoring:** Approximately 30% of data is **right-censored** (values above a threshold are marked as `>Threshold`).
    """
    utils.create_report(description=description)

if __name__ == "__main__":
    # Seed for reproducibility
    np.random.seed(123)
    run()
