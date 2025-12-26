import os
import sys
import numpy as np
import pandas as pd

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from validation.validation_utils import ValidationUtils

def generate_numeric_time_data(n=20, slope=1.0, noise_std=0.5, start_year=2000):
    """Generates annual data with a simple linear trend using numeric time vector."""
    # Create numeric time with decimal parts to simulate non-integer years if needed
    t = np.sort(np.random.uniform(start_year, start_year + n, n))

    noise = np.random.normal(0, noise_std, n)
    # y = slope * (t - start_year) + 10
    values = slope * (t - start_year) + 10 + noise

    return pd.DataFrame({'time': t, 'value': values})

def run():
    utils = ValidationUtils(os.path.dirname(__file__))
    scenarios = []

    # Scenario 1: Strong Increasing Trend
    df_strong = generate_numeric_time_data(n=20, slope=2.0, noise_std=1.0)
    _, mk_std_strong = utils.run_comparison(
        test_id="V-06",
        df=df_strong,
        scenario_name="strong_increasing",
        true_slope=2.0
    )
    scenarios.append({
        'df': df_strong,
        'title': 'Strong Increasing (Numeric Time)',
        'mk_result': mk_std_strong
    })

    # Scenario 2: Weak Decreasing Trend
    df_weak = generate_numeric_time_data(n=20, slope=-0.2, noise_std=1.0)
    _, mk_std_weak = utils.run_comparison(
        test_id="V-06",
        df=df_weak,
        scenario_name="weak_decreasing",
        true_slope=-0.2
    )
    scenarios.append({
        'df': df_weak,
        'title': 'Weak Decreasing (Numeric Time)',
        'mk_result': mk_std_weak
    })

    # Scenario 3: Stable (No Trend)
    df_stable = generate_numeric_time_data(n=20, slope=0.0, noise_std=1.0)
    _, mk_std_stable = utils.run_comparison(
        test_id="V-06",
        df=df_stable,
        scenario_name="stable",
        true_slope=0.0
    )
    scenarios.append({
        'df': df_stable,
        'title': 'Stable (Numeric Time)',
        'mk_result': mk_std_stable
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v06_combined.png", "V-06: Numeric Time Vector Analysis")

    # Generate Report
    utils.create_report()

if __name__ == "__main__":
    # Seed for reproducibility
    np.random.seed(42)
    run()
