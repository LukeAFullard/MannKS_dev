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
    final_values[censored] = threshold

    df = pd.DataFrame({
        'date': dates,
        'value': final_values,
        'censored': censored,
        'cen_type': cen_type,
        'true_value': values # For debugging
    })

    return df

def run():
    utils = LeftCensoredValidationUtils(os.path.dirname(__file__))

    # Scenario 1: Strong Increasing Trend
    # Slope 5.0, Noise 1.0, Intercept 10
    # Higher slope to distinguish from previous test
    df_strong = generate_left_censored_data(n=36, slope=5.0, noise_std=1.0, censor_threshold_percentile=20, intercept=10)

    _, mk_std = utils.run_comparison(
        test_id="V-08",
        df=df_strong,
        scenario_name="strong_increasing",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=5.0
    )

    utils.generate_plot(df_strong, "V-08 Strong Increasing Trend (Left Censored)", "v08_strong_left_censored.png", mk_result=mk_std)

    # Scenario 2: Weak Decreasing Trend
    # Slope -0.8, Noise 0.5, Intercept 20
    # Lower noise and higher intercept to ensure detectable negative trend without negative data artifacts
    df_weak = generate_left_censored_data(n=36, slope=-0.8, noise_std=0.5, censor_threshold_percentile=20, intercept=20)
    utils.run_comparison(
        test_id="V-08",
        df=df_weak,
        scenario_name="weak_decreasing",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=-0.8
    )

    # Scenario 3: Stable (No Trend)
    # Slope 0.0, Noise 1.0, Intercept 15
    df_stable = generate_left_censored_data(n=36, slope=0.0, noise_std=1.0, censor_threshold_percentile=20, intercept=15)
    utils.run_comparison(
        test_id="V-08",
        df=df_stable,
        scenario_name="stable",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=0.0
    )

    # Generate Report
    description = """
    # V-08: Left-Censored Trend

    This validation case tests the package's ability to handle left-censored data (values reported as less than a detection limit, e.g., `<5.0`).

    Three scenarios were tested with updated parameters to ensure robust detectability:
    1. **Strong Increasing Trend**: Slope 5.0, Noise 1.0. Clear positive trend.
    2. **Weak Decreasing Trend**: Slope -0.8, Noise 0.5. Detectable negative trend (avoiding zero-slope artifacts from high noise).
    3. **Stable (No Trend)**: Slope 0.0, Noise 1.0. No underlying trend.

    Comparison is made between:
    - **MannKenSen (Standard)**: Uses the 'robust' method for Mann-Kendall and Sen's slope.
    - **MannKenSen (LWP Mode)**: Uses `mk_test_method='lwp'` and `agg_method='lwp'` to mimic R.
    - **LWP-TRENDS R Script**: The reference implementation.
    - **MannKenSen (ATS)**: Uses the Akritas-Theil-Sen estimator.
    - **NADA2 R Script**: Using the ATS estimator (reference for ATS mode).
    """

    utils.create_report(description=description)

if __name__ == "__main__":
    np.random.seed(101) # New seed for new data
    run()
