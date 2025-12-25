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

def generate_tied_data(n=20, slope=1.0, noise_std=0.5, start_year=2000):
    """Generates monthly data with ties."""
    dates = pd.date_range(start=f'{start_year}-01-01', periods=n, freq='ME') # Month End
    t = np.arange(n)
    noise = np.random.normal(0, noise_std, n)
    values = slope * t + 10 + noise

    # Introduce ties by rounding
    values = np.round(values / 2) * 2

    return pd.DataFrame({'date': dates, 'value': values})

def run():
    utils = ValidationUtils(os.path.dirname(__file__))

    # Scenario 1: Strong Increasing with Ties
    # NOTE: slope=0.1 per month. Annual slope ~ 1.2
    # The LWP R logic uses Years as time unit for slope.
    # MannKenSen using date objects also outputs per Year (or whatever unit dates imply, which is 365.25 days).
    # So true slope is 0.1 * 12 = 1.2
    df_strong = generate_tied_data(n=60, slope=0.1, noise_std=2.0)
    _, mk_std = utils.run_comparison(
        test_id="V-02",
        df=df_strong,
        scenario_name="strong_increasing_tied",
        true_slope=1.2
    )
    utils.generate_plot(df_strong, "V-02 Strong Increasing (Tied)", "v02_strong.png", mk_result=mk_std)

    # Scenario 2: Weak Decreasing with Ties
    # Slope -0.05 per month -> -0.6 per year
    df_weak = generate_tied_data(n=60, slope=-0.05, noise_std=2.0)
    utils.run_comparison(
        test_id="V-02",
        df=df_weak,
        scenario_name="weak_decreasing_tied",
        true_slope=-0.6
    )

    # Scenario 3: Stable with Ties (Many ties expected)
    df_stable = generate_tied_data(n=60, slope=0.0, noise_std=1.0)
    utils.run_comparison(
        test_id="V-02",
        df=df_stable,
        scenario_name="stable_tied",
        true_slope=0.0
    )

    # Generate Report
    utils.create_report()

if __name__ == "__main__":
    np.random.seed(42)
    run()
