
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import MannKenSen as mk
from validation.validation_utils import ValidationUtils

# Initialize ValidationUtils
output_dir = os.path.dirname(__file__)
utils = ValidationUtils(output_dir)

# Define test case parameters
TEST_ID = "V-14"
DESCRIPTION = """
**V-14: Monthly Seasonal Trend**

This test verifies the seasonal trend analysis functionality on a simple monthly dataset.
It compares the standard `mannkensen` seasonal test against the LWP-TRENDS R script and NADA2.

**Scenarios:**
1.  **Strong Increasing:** Clear positive trend with seasonality.
2.  **Weak Decreasing:** Subtle negative trend with seasonality.
3.  **Stable:** No underlying trend, just seasonality.
"""

def generate_seasonal_data(n_years=10, start_year=2000, trend_slope=0.0, noise_std=1.0, season_amp=5.0):
    """Generates monthly seasonal data."""
    dates = []
    values = []

    for year in range(start_year, start_year + n_years):
        for month in range(1, 13):
            date = datetime(year, month, 15) # Mid-month

            # Time in years for trend calculation
            t_year = year + (month - 1) / 12.0

            # Trend component
            trend_val = trend_slope * (t_year - start_year)

            # Seasonal component (sine wave)
            season_val = season_amp * np.sin(2 * np.pi * (month - 1) / 12.0)

            # Noise
            noise = np.random.normal(0, noise_std)

            val = 100 + trend_val + season_val + noise

            dates.append(date)
            values.append(val)

    return pd.DataFrame({'date': dates, 'value': values})

# --- Run Scenarios ---

scenarios_to_plot = []

# 1. Strong Increasing Trend
df_inc = generate_seasonal_data(n_years=10, trend_slope=2.0, noise_std=1.0)
res_inc, mk_std_inc = utils.run_comparison(
    TEST_ID, df_inc, "strong_increasing",
    seasonal=True,
    mk_kwargs={'season_type': 'month', 'period': 12, 'slope_scaling': 'year'},
    lwp_mode_kwargs={'season_type': 'month', 'period': 12},
    true_slope=2.0
)
# Fix for plotting: If slope_scaling is used, slope is per year.
# But ValidationUtils handles plotting with logic that might need adjustment.
# The `run_comparison` returns `mk_std` which now has `scaled_slope` in `.slope`.
# `validation_utils.py` uses `t_numeric` (years) * `slope` + `intercept`.
# Since `slope` is now units/year, this dimensionally matches.
# BUT `intercept` in `seasonal_trend_test` is calculated as `mean(y) - mean(t_seconds) * raw_slope`.
# Wait, let's look at `seasonal_trend_test.py` again.
# `intercept = np.nanmedian(data_filtered['value']) - np.nanmedian(data_filtered['t']) * slope`
# where `slope` is raw slope (per second) and `t` is seconds.
# So `intercept` is correct for `y = raw_slope * t_sec + intercept`.
# It is NOT correct for `y = scaled_slope * t_year + intercept`.
# So using scaled slope with standard intercept and t_year will fail.

# To fix this locally for this specific plot without breaking utils or package code:
# I will modify the mk_result object before passing it to plotting.
# I will recalculate intercept for the yearly time scale.

def fix_mk_result_for_plotting(mk_res, df):
    # Calculate t in years
    dates = pd.to_datetime(df['date'])
    t_years = (dates - pd.Timestamp("1970-01-01")).dt.days / 365.25
    t_years = t_years.values

    y = df['value'].values
    slope = mk_res.slope # This is scaled slope (per year)

    # Recalculate intercept for y = m*t_years + c
    # Using median pivot point like Sen's method
    t_med = np.median(t_years)
    y_med = np.median(y)
    intercept_year = y_med - slope * t_med

    # Create a new namedtuple with modified intercept
    # We can't modify tuple, so we use _replace
    return mk_res._replace(intercept=intercept_year)

mk_std_inc_plot = fix_mk_result_for_plotting(mk_std_inc, df_inc)
scenarios_to_plot.append({'df': df_inc, 'title': 'Strong Increasing Trend', 'mk_result': mk_std_inc_plot})


# 2. Weak Decreasing Trend
df_dec = generate_seasonal_data(n_years=10, trend_slope=-0.5, noise_std=2.0)
res_dec, mk_std_dec = utils.run_comparison(
    TEST_ID, df_dec, "weak_decreasing",
    seasonal=True,
    mk_kwargs={'season_type': 'month', 'period': 12, 'slope_scaling': 'year'},
    lwp_mode_kwargs={'season_type': 'month', 'period': 12},
    true_slope=-0.5
)
mk_std_dec_plot = fix_mk_result_for_plotting(mk_std_dec, df_dec)
scenarios_to_plot.append({'df': df_dec, 'title': 'Weak Decreasing Trend', 'mk_result': mk_std_dec_plot})


# 3. Stable (No Trend)
df_stab = generate_seasonal_data(n_years=10, trend_slope=0.0, noise_std=1.0)
res_stab, mk_std_stab = utils.run_comparison(
    TEST_ID, df_stab, "stable",
    seasonal=True,
    mk_kwargs={'season_type': 'month', 'period': 12, 'slope_scaling': 'year'},
    lwp_mode_kwargs={'season_type': 'month', 'period': 12},
    true_slope=0.0
)
mk_std_stab_plot = fix_mk_result_for_plotting(mk_std_stab, df_stab)
scenarios_to_plot.append({'df': df_stab, 'title': 'Stable (No Trend)', 'mk_result': mk_std_stab_plot})

# --- Generate Outputs ---

# 1. Combined Plot (MKS Standard only)
utils.generate_combined_plot(scenarios_to_plot, "V14_Trend_Analysis.png", "V-14: Monthly Seasonal Trend Analysis")

# 2. Report
utils.create_report("README.md", DESCRIPTION)
