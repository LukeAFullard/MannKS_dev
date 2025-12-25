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
    # Determine a threshold that censors roughly censor_pct of the data
    # For right censoring, we censor values ABOVE the threshold.
    # To censor the top 30%, we set the threshold at the 70th percentile.
    threshold = np.percentile(base_values, (1 - censor_pct) * 100)

    final_values = []
    for v in base_values:
        if v > threshold:
            # Create a right-censored string.
            # LWP script expects ">Threshold".
            # To make it realistic, we might vary the threshold or keep it constant.
            # LWP usually deals with detection limits which are constant or change in steps.
            # For right censoring (often "Too Numerous To Count"), it might be a constant upper limit.
            final_values.append(f">{threshold:.1f}")
        else:
            final_values.append(v)

    return pd.DataFrame({'date': dates, 'value': final_values})

def generate_plot_custom(df, title, filename, output_dir, mk_result=None):
    """
    Generates a plot showing ONLY Raw Data and MKS Standard Trend/CI.
    Ignores censored nature in plotting logic (just plots parsed values)
    but distinguishes them visually if desired (User said "raw data", usually implies distinguishing).
    However, the user said "single plot only including raw data and the MKS (standard) trend".
    """
    plt.figure(figsize=(10, 6))

    # Parse values for plotting
    y_plot = []
    colors = []

    for v in df['value']:
        if isinstance(v, str) and ('>' in v or '<' in v):
            val = float(v.replace('>', '').replace('<', ''))
            y_plot.append(val)
            colors.append('red') # Censored
        else:
            y_plot.append(float(v))
            colors.append('black') # Observed

    x_plot = df['date']

    # Plot Data Points
    # Split into censored and uncensored for legend
    x_obs = [x for x, c in zip(x_plot, colors) if c == 'black']
    y_obs = [y for y, c in zip(y_plot, colors) if c == 'black']
    x_cen = [x for x, c in zip(x_plot, colors) if c == 'red']
    y_cen = [y for y, c in zip(y_plot, colors) if c == 'red']

    plt.plot(x_obs, y_obs, 'o', color='black', label='Observed')
    plt.plot(x_cen, y_cen, 'o', color='red', markerfacecolor='none', label='Censored')

    # Plot MKS Standard Trend
    if mk_result is not None:
        # Get numeric time for calculation
        dates_pd = pd.to_datetime(df['date'])
        t_numeric = dates_pd.dt.year + (dates_pd.dt.dayofyear - 1) / 365.25
        t_numeric = t_numeric.values

        # Calculate Trend Line
        # Slope is in units/year if using the helper's numeric time conversion logic?
        # mk_result comes from MKS standard run.
        # If we passed datetime to MKS, slope is per second.
        # But ValidationUtils.run_comparison passes NUMERIC time (years) to MKS Standard.
        # So slope is per year.

        y_trend = mk_result.slope * t_numeric + mk_result.intercept
        plt.plot(x_plot, y_trend, '-', color='blue', label=f"Sen's Slope: {mk_result.slope:.4f}")

        # CIs
        t_med = np.median(t_numeric)
        y_med = np.median(y_plot)

        if not np.isnan(mk_result.lower_ci):
            y_lower = mk_result.lower_ci * (t_numeric - t_med) + y_med
            plt.plot(x_plot, y_lower, '--', color='blue', alpha=0.5, label='90% CI')

        if not np.isnan(mk_result.upper_ci):
            y_upper = mk_result.upper_ci * (t_numeric - t_med) + y_med
            plt.plot(x_plot, y_upper, '--', color='blue', alpha=0.5)
            plt.fill_between(x_plot, y_lower, y_upper, color='blue', alpha=0.1)

    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)

    plot_path = os.path.join(output_dir, filename)
    plt.savefig(plot_path)
    plt.close()
    print(f"Plot saved to {plot_path}")

def run():
    # Use the specific output directory
    output_dir = os.path.join(repo_root, 'validation', '13_Censored_LWP_Modes')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    utils = ValidationUtils(output_dir)

    # Define LWP kwargs for this specific validation case
    # This ensures we are testing the "LWP Mode" specifically
    lwp_kwargs = {
        'mk_test_method': 'lwp',
        'ci_method': 'lwp',
        'sens_slope_method': 'lwp',
        'lt_mult': 0.5,
        'gt_mult': 1.1, # LWP uses 1.1 for GT censored in Sen's slope pairs (sometimes)
        # ValidationUtils.run_comparison sets defaults, but we can override.
        # The key for V-13 is verifying 'mk_test_method' and 'sens_slope_method' behavior.
    }

    # Scenario 1: Strong Increasing Trend (Right Censored)
    # n=48 (4 years of monthly data)
    print("Generating Scenario 1: Strong Increasing")
    df_strong = generate_censored_data(n=48, slope=2.0, noise_std=1.0, censor_pct=0.3)

    # Run Comparison
    # Note: validation_utils.run_comparison handles the 5-way test.
    # We pass the lwp_kwargs to configure the "LWP Mode" run.
    res_strong, mk_std_strong = utils.run_comparison(
        test_id="V-13",
        df=df_strong,
        scenario_name="strong_increasing",
        lwp_mode_kwargs=lwp_kwargs,
        true_slope=2.0
    )

    # Generate the single requested plot
    generate_plot_custom(
        df_strong,
        "V-13 Strong Increasing Trend (Right-Censored)",
        "v13_strong.png",
        output_dir,
        mk_result=mk_std_strong
    )

    # Scenario 2: Weak Decreasing Trend
    print("Generating Scenario 2: Weak Decreasing")
    df_weak = generate_censored_data(n=48, slope=-0.2, noise_std=1.0, censor_pct=0.3)
    utils.run_comparison(
        test_id="V-13",
        df=df_weak,
        scenario_name="weak_decreasing",
        lwp_mode_kwargs=lwp_kwargs,
        true_slope=-0.2
    )

    # Scenario 3: Stable (No Trend)
    print("Generating Scenario 3: Stable")
    df_stable = generate_censored_data(n=48, slope=0.0, noise_std=1.0, censor_pct=0.3)
    utils.run_comparison(
        test_id="V-13",
        df=df_stable,
        scenario_name="stable",
        lwp_mode_kwargs=lwp_kwargs,
        true_slope=0.0
    )

    # Generate Report
    description = """
# Validation Case V-13: Censored LWP Compatibility Modes

This validation case focuses on verifying the "LWP Compatibility Mode" of the `mannkensen` package against the original LWP-TRENDS R script, specifically for **right-censored** data.

The goal is to demonstrate that setting parameters `mk_test_method='lwp'` and `sens_slope_method='lwp'` allows Python to accurately replicate the R script's handling of censored values.

## Methodology
- **Data:** 4 years of monthly data (n=48).
- **Censoring:** Approximately 30% of data is **right-censored** (values above a threshold are marked as `>Threshold`).
- **Comparisons:**
    1. **MannKenSen (Standard):** Uses 'robust' MK test and standard Sen's slope.
    2. **MannKenSen (LWP Mode):** Uses `mk_test_method='lwp'` and `sens_slope_method='lwp'`.
    3. **LWP-TRENDS (R):** The reference R script.
    4. **MannKenSen (ATS):** Akritas-Theil-Sen method.
    5. **NADA2 (R):** The NADA2 reference R script.

**Note:** The plot below displays the **Standard** MannKenSen results on the raw data, as requested.
    """
    utils.create_report(description=description)

if __name__ == "__main__":
    # Seed for reproducibility
    np.random.seed(123)
    run()
