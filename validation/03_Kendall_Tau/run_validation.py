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
import MannKenSen as mk

def generate_highly_tied_data(n=30, trend='step'):
    """Generates data with many ties."""
    dates = pd.date_range(start='2000-01-01', periods=n, freq='ME')

    if trend == 'step_up':
        # Step function increasing
        values = np.zeros(n)
        values[10:20] = 5
        values[20:] = 10
    elif trend == 'step_down':
        # Step function decreasing
        values = np.zeros(n) + 10
        values[10:20] = 5
        values[20:] = 0
    else: # Flat
        values = np.zeros(n) + 5

    return pd.DataFrame({'date': dates, 'value': values})

def run():
    utils = ValidationUtils(os.path.dirname(__file__))
    scenarios = []

    # Scenario 1: Step Up (Increasing)
    df_step_up = generate_highly_tied_data(trend='step_up')
    _, mk_res_up = utils.run_comparison(
        test_id="V-03",
        df=df_step_up,
        scenario_name="step_increasing",
        mk_kwargs={'tau_method': 'b'},
        true_slope=5.0 # Roughly
    )
    scenarios.append({
        'df': df_step_up,
        'title': 'Step Increasing (Tau-b)',
        'mk_result': mk_res_up
    })

    # Scenario 2: Step Down (Decreasing)
    df_step_down = generate_highly_tied_data(trend='step_down')
    _, mk_res_down = utils.run_comparison(
        test_id="V-03",
        df=df_step_down,
        scenario_name="step_decreasing",
        mk_kwargs={'tau_method': 'b'},
        true_slope=-5.0
    )
    scenarios.append({
        'df': df_step_down,
        'title': 'Step Decreasing (Tau-b)',
        'mk_result': mk_res_down
    })

    # Scenario 3: Flat (No Trend)
    df_flat = generate_highly_tied_data(trend='flat')
    _, mk_res_flat = utils.run_comparison(
        test_id="V-03",
        df=df_flat,
        scenario_name="flat",
        mk_kwargs={'tau_method': 'b'},
        true_slope=0.0
    )
    scenarios.append({
        'df': df_flat,
        'title': 'Flat (Tau-b)',
        'mk_result': mk_res_flat
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v03_combined.png", "V-03: Kendall Tau Analysis (Highly Tied)")

    # Additional Tau-a check (keep logic but no plot for this specific sub-test in main figure)
    # Just running it for the table
    utils.run_comparison(
        test_id="V-03",
        df=df_step_up,
        scenario_name="step_increasing_tau_a",
        mk_kwargs={'tau_method': 'a'},
        true_slope=5.0
    )

    # Generate Report
    utils.create_report()

if __name__ == "__main__":
    np.random.seed(42)
    run()
