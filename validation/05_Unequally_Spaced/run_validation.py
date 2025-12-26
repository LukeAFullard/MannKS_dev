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

def generate_unequal_trend_data(n=20, slope=1.0, noise_std=0.5, start_year=2000):
    """
    Generates data with one observation per year, but at random dates within the year.
    This creates an unequally spaced time series while ensuring compatibility with
    the LWP R script's 'Year' based logic (which often assumes annual steps).
    """
    years = np.arange(start_year, start_year + n)
    # Random day of year (1 to 365)
    days_of_year = np.random.randint(1, 365, size=n)

    dates = []
    t_numeric = []

    for y, d in zip(years, days_of_year):
        dt = datetime(y, 1, 1) + timedelta(days=int(d) - 1)
        dates.append(dt)
        # Decimal year for exact calculation
        t_numeric.append(y + (d - 1) / 365.25)

    t_numeric = np.array(t_numeric)

    # Generate values based on EXACT time
    noise = np.random.normal(0, noise_std, n)
    values = slope * t_numeric + 10 + noise

    return pd.DataFrame({'date': dates, 'value': values})

def run():
    utils = ValidationUtils(os.path.dirname(__file__))
    scenarios = []

    description = """
**V-05: Unequally Spaced Time Series**

*   **Objective:** Verify a core feature of `mannkensen` on a non-seasonal, unequally spaced time series.
*   **Data Description:** Data with a clear trend but with random, non-uniform time gaps between samples. This test highlights a key methodological difference where the R script is expected to differ.
    """

    # Scenario 1: Strong Increasing Trend
    df_strong = generate_unequal_trend_data(n=20, slope=2.0, noise_std=0.5)

    _, mk_std_strong = utils.run_comparison(
        test_id="V-05",
        df=df_strong,
        scenario_name="strong_increasing",
        true_slope=2.0
    )
    scenarios.append({
        'df': df_strong,
        'title': 'Strong Increasing (Unequal)',
        'mk_result': mk_std_strong
    })

    # Scenario 2: Weak Decreasing Trend
    df_weak = generate_unequal_trend_data(n=20, slope=-0.2, noise_std=0.5)
    _, mk_std_weak = utils.run_comparison(
        test_id="V-05",
        df=df_weak,
        scenario_name="weak_decreasing",
        true_slope=-0.2
    )
    scenarios.append({
        'df': df_weak,
        'title': 'Weak Decreasing (Unequal)',
        'mk_result': mk_std_weak
    })

    # Scenario 3: Stable (No Trend)
    df_stable = generate_unequal_trend_data(n=20, slope=0.0, noise_std=0.5)
    _, mk_std_stable = utils.run_comparison(
        test_id="V-05",
        df=df_stable,
        scenario_name="stable",
        true_slope=0.0
    )
    scenarios.append({
        'df': df_stable,
        'title': 'Stable (Unequal)',
        'mk_result': mk_std_stable
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v05_combined.png", "V-05: Unequally Spaced Analysis")

    # Generate Report
    utils.create_report(description=description)

if __name__ == "__main__":
    # Seed for reproducibility
    np.random.seed(42)
    run()
