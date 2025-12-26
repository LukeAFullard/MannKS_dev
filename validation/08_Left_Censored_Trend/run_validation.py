import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Dict, Tuple

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from validation.validation_utils import ValidationUtils
import MannKenSen as mk
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.conversion import localconverter

class LeftCensoredValidationUtils(ValidationUtils):
    """
    Subclass of ValidationUtils to explicitly handle left-censored data generation and plotting.
    Uses the default _prepare_r_dataframe which assumes left-censoring logic (RawValue, Censored, CenType='lt').
    """
    pass

def generate_left_censored_data(n=24, slope=1.0, noise_std=0.5, start_year=2000,
                                censor_threshold_percentile=20, intercept=10):
    """
    Generates monthly data with a trend and left-censoring.
    Values below the threshold are marked as censored (<).
    """
    dates = pd.date_range(start=f'{start_year}-01-01', periods=n, freq='ME')
    t = np.arange(n) / 12.0 # Yearly time steps
    noise = np.random.normal(0, noise_std, n)
    values = slope * t + intercept + noise

    threshold = np.percentile(values, censor_threshold_percentile)

    censored = values < threshold
    cen_type = np.where(censored, 'lt', 'not')

    # For left censored values, the reported value is the threshold (limit).
    # e.g. if real value is 2 and limit is 5, we report <5.
    final_values = values.copy()

    # Create the mixed type column
    final_values = final_values.astype(object)
    final_values[censored] = '<' + str(threshold)

    df = pd.DataFrame({
        'date': dates,
        'value': final_values,
        'cen_type': cen_type, # Helper for plotting color
        'true_value': values # For debugging
    })

    return df

def run():
    utils = LeftCensoredValidationUtils(os.path.dirname(__file__))
    scenarios = []

    # Scenario 1: Strong Increasing Trend
    df_strong = generate_left_censored_data(n=36, slope=5.0, noise_std=1.0, censor_threshold_percentile=20, intercept=10)

    _, mk_std_strong = utils.run_comparison(
        test_id="V-08",
        df=df_strong,
        scenario_name="strong_increasing",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=5.0
    )
    scenarios.append({
        'df': df_strong,
        'title': 'Strong Increasing (Left Censored)',
        'mk_result': mk_std_strong
    })

    # Scenario 2: Weak Decreasing Trend
    df_weak = generate_left_censored_data(n=36, slope=-0.8, noise_std=0.5, censor_threshold_percentile=20, intercept=20)
    _, mk_std_weak = utils.run_comparison(
        test_id="V-08",
        df=df_weak,
        scenario_name="weak_decreasing",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=-0.8
    )
    scenarios.append({
        'df': df_weak,
        'title': 'Weak Decreasing (Left Censored)',
        'mk_result': mk_std_weak
    })

    # Scenario 3: Stable (No Trend)
    df_stable = generate_left_censored_data(n=36, slope=0.0, noise_std=1.0, censor_threshold_percentile=20, intercept=15)
    _, mk_std_stable = utils.run_comparison(
        test_id="V-08",
        df=df_stable,
        scenario_name="stable",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=0.0
    )
    scenarios.append({
        'df': df_stable,
        'title': 'Stable (Left Censored)',
        'mk_result': mk_std_stable
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v08_combined.png", "V-08: Left-Censored Trend Analysis")

    # Generate Report
    description = """
    # V-08: Left-Censored Trend

    This validation case tests the package's ability to handle left-censored data (values reported as less than a detection limit, e.g., `<5.0`).

    Three scenarios were tested with updated parameters to ensure robust detectability:
    1. **Strong Increasing Trend**: Slope 5.0, Noise 1.0. Clear positive trend.
    2. **Weak Decreasing Trend**: Slope -0.8, Noise 0.5. Detectable negative trend (avoiding zero-slope artifacts from high noise).
    3. **Stable (No Trend)**: Slope 0.0, Noise 1.0. No underlying trend.
    """

    utils.create_report(description=description)

if __name__ == "__main__":
    np.random.seed(101) # New seed for new data
    run()
