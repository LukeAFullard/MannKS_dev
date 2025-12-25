
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Add repo root to path to ensure MannKenSen can be imported
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import Validation Utils
sys.path.append(os.path.join(repo_root, 'validation'))
from validation_utils import ValidationUtils

# Initialize Validation Utilities
output_dir = os.path.dirname(__file__)
validator = ValidationUtils(output_dir)

# --- Data Generation Helper ---
def generate_mixed_censored_data(n=60, trend_slope=0.1, noise_std=0.5, censor_fraction=0.3):
    """
    Generates synthetic monthly data with a linear trend and mixed censoring.
    """
    np.random.seed(42)  # Fixed seed for reproducibility
    dates = [datetime(2000, 1, 1) + timedelta(days=30*i) for i in range(n)]

    # Base signal: Trend + Noise
    t = np.arange(n)
    y_raw = trend_slope * t + np.random.normal(0, noise_std, n)

    # Create DataFrame
    df = pd.DataFrame({'date': dates, 'value': y_raw})

    # Apply Censoring
    # Select indices to censor
    n_censored = int(n * censor_fraction)
    censor_indices = np.random.choice(n, n_censored, replace=False)

    # Split censored indices into Left (<) and Right (>)
    n_left = int(n_censored / 2)
    left_indices = censor_indices[:n_left]
    right_indices = censor_indices[n_left:]

    # Convert 'value' column to object to hold strings
    df['value'] = df['value'].astype(object)

    # Apply Left Censoring (e.g., < 2.0)
    # To make it realistic, we round up the actual value slightly and mark as <
    for idx in left_indices:
        val = df.loc[idx, 'value']
        limit = np.ceil(val * 10) / 10.0  # Round up to nearest 0.1
        if limit < val: limit += 0.1 # Ensure limit > val
        df.loc[idx, 'value'] = f"<{limit:.1f}"

    # Apply Right Censoring (e.g., > 5.0)
    # To make it realistic, we round down slightly and mark as >
    for idx in right_indices:
        val = df.loc[idx, 'value']
        limit = np.floor(val * 10) / 10.0 # Round down to nearest 0.1
        if limit > val: limit -= 0.1
        df.loc[idx, 'value'] = f">{limit:.1f}"

    return df

# --- Scenarios ---

# 1. Strong Increasing Trend
df_strong = generate_mixed_censored_data(n=60, trend_slope=0.2, noise_std=1.0, censor_fraction=0.3)
res_strong, mk_strong = validator.run_comparison(
    test_id="V-10",
    df=df_strong,
    scenario_name="Strong_Increasing",
    mk_kwargs={},
    lwp_mode_kwargs={'mk_test_method': 'lwp', 'ci_method': 'lwp', 'sens_slope_method': 'lwp'},
    true_slope=0.2
)

# Generate Plot ONLY for Strong Increasing (as requested)
validator.generate_plot(df_strong, "V-10: Mixed Censoring - Strong Increasing Trend", "V-10_strong_increasing_plot.png", mk_result=mk_strong)

# 2. Weak Decreasing Trend
df_weak = generate_mixed_censored_data(n=60, trend_slope=-0.05, noise_std=1.5, censor_fraction=0.3)
validator.run_comparison(
    test_id="V-10",
    df=df_weak,
    scenario_name="Weak_Decreasing",
    mk_kwargs={},
    lwp_mode_kwargs={'mk_test_method': 'lwp', 'ci_method': 'lwp', 'sens_slope_method': 'lwp'},
    true_slope=-0.05
)

# 3. Stable (No Trend)
df_stable = generate_mixed_censored_data(n=60, trend_slope=0.0, noise_std=1.0, censor_fraction=0.3)
validator.run_comparison(
    test_id="V-10",
    df=df_stable,
    scenario_name="Stable",
    mk_kwargs={},
    lwp_mode_kwargs={'mk_test_method': 'lwp', 'ci_method': 'lwp', 'sens_slope_method': 'lwp'},
    true_slope=0.0
)

# --- Generate Report ---
validator.create_report("README.md")

print("V-10 Validation Complete.")
