import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from validation.validation_utils import ValidationUtils

def generate_simple_trend_data(n=20, slope=1.0, noise_std=0.5, start_year=2000):
    """Generates annual data with a simple linear trend."""
    dates = [datetime(start_year + i, 1, 1) for i in range(n)]
    t = np.arange(n)
    noise = np.random.normal(0, noise_std, n)
    values = slope * t + 10 + noise # +10 offset

    return pd.DataFrame({'date': dates, 'value': values})

def run():
    utils = ValidationUtils(os.path.dirname(__file__))

    # Scenario 1: Strong Increasing Trend
    df_strong = generate_simple_trend_data(n=20, slope=2.0, noise_std=1.0)
    _, mk_std = utils.run_comparison(
        test_id="V-01",
        df=df_strong,
        scenario_name="strong_increasing",
        true_slope=2.0
    )
    utils.generate_plot(df_strong, "V-01 Strong Increasing Trend", "v01_strong.png", mk_result=mk_std)

    # Scenario 2: Weak Decreasing Trend
    df_weak = generate_simple_trend_data(n=20, slope=-0.2, noise_std=1.0)
    utils.run_comparison(
        test_id="V-01",
        df=df_weak,
        scenario_name="weak_decreasing",
        true_slope=-0.2
    )

    # Scenario 3: Stable (No Trend)
    df_stable = generate_simple_trend_data(n=20, slope=0.0, noise_std=1.0)
    utils.run_comparison(
        test_id="V-01",
        df=df_stable,
        scenario_name="stable",
        true_slope=0.0
    )

    # Generate Report
    utils.create_report()

if __name__ == "__main__":
    # Seed for reproducibility
    np.random.seed(42)
    run()
