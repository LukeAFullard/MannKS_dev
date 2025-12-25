
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import MannKenSen as mk
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
from rpy2.robjects.conversion import localconverter

# Ensure we can import the validation helpers if they existed, but I'll self-contain for now
# based on previous patterns.

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(OUTPUT_DIR, "README.md")
MASTER_CSV_PATH = os.path.join(os.path.dirname(OUTPUT_DIR), "master_results.csv")
PLOT_PATH = os.path.join(OUTPUT_DIR, "plot_trend.png")

def generate_sensitive_data(scenario):
    """
    Generates synthetic data with multiple censoring levels (<1, <3, <5).
    The data is designed to be sensitive to the multiplier value.
    """
    np.random.seed(42)
    n = 24  # 2 years of monthly data
    t = pd.date_range(start='2020-01-01', periods=n, freq='ME')

    # Base values
    if scenario == 'strong_increasing':
        # Trend from low (censored) to high
        # Start around 0.5, end around 10
        values = np.linspace(0.5, 10, n)
    elif scenario == 'weak_decreasing':
        # Trend from moderate to low (censored)
        # Start around 6, end around 0.5
        values = np.linspace(6, 0.5, n)
    elif scenario == 'stable':
        # Stable around 2.0 (mix of censored/uncensored)
        values = np.random.normal(2.0, 1.5, n)

    # Add noise
    noise = np.random.normal(0, 0.5, n)
    values = values + noise

    # Apply multiple censoring limits
    # We want a mix of <1, <3, <5
    censored_values = []

    for v in values:
        if v < 1.0:
            censored_values.append("<1")
        elif v < 3.0:
            # Randomly censor some values between 1 and 3 as <3
            if np.random.random() > 0.3:
                censored_values.append("<3")
            else:
                censored_values.append(f"{v:.3f}")
        elif v < 5.0:
             # Randomly censor some values between 3 and 5 as <5
            if np.random.random() > 0.7:
                censored_values.append("<5")
            else:
                censored_values.append(f"{v:.3f}")
        else:
            censored_values.append(f"{v:.3f}")

    return pd.Series(censored_values), t

def run_r_lwp(df, mk_test_method='lwp'):
    """Runs the LWP-TRENDS R script."""
    # Convert data to R format
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df)

    # Source the R script
    r_script_path = os.path.abspath(os.path.join(OUTPUT_DIR, "../../Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r"))
    r.source(r_script_path)

    # Pre-process in R
    r.assign('data', r_df)
    r("""
    data_processed <- RemoveAlphaDetect(data, ColToUse="value")
    # Add dummy date columns required by LWP
    data_processed$myDate <- as.Date(data$t)
    data_processed <- GetMoreDateInfo(data_processed)
    # Filter for trend
    data_final <- InspectTrendData(data_processed)
    """)

    # Run Analysis
    # Note: LWP R script defaults to lt_mult=0.5, gt_mult=1.1 inside SenSlope
    try:
        r("""
        result <- NonSeasonalTrendAnalysis(data_final, do.plot=FALSE)
        """)
        r_result = r['result']

        # Extract results - result is a list/dataframe
        # LWP returns a dataframe with columns like 'Slope', 'PVal', etc.
        # Check column names
        cols = list(r_result.colnames)

        # Correct column names for LWP v2502
        slope_col = 'AnnualSenSlope'
        p_col = 'p'
        lci_col = 'Sen_Lci'
        uci_col = 'Sen_Uci'

        if slope_col not in cols:
            print(f"Warning: '{slope_col}' not found in R results. Columns are: {cols}")
            # Fallback attempts
            if 'Slope' in cols: slope_col = 'Slope'

        if p_col not in cols and 'PVal' in cols: p_col = 'PVal'

        try:
            slope = r_result.rx2(slope_col)[0]
            p = r_result.rx2(p_col)[0]
            lower_ci = r_result.rx2(lci_col)[0] if lci_col in cols else np.nan
            upper_ci = r_result.rx2(uci_col)[0] if uci_col in cols else np.nan
            return slope, p, lower_ci, upper_ci
        except Exception as e:
            print(f"Error extracting columns from R result: {e}")
            print(f"Available columns: {cols}")
            return np.nan, np.nan, np.nan, np.nan

    except Exception as e:
        print(f"R LWP Execution Failed: {e}")
        return np.nan, np.nan, np.nan, np.nan

def run_r_nada(df):
    """Runs the NADA ATS method."""
    with localconverter(ro.default_converter + pandas2ri.converter):
        r_df = ro.conversion.py2rpy(df)

    # Source the ATS script and kenplot from NADA2 folder
    ats_script_path = os.path.abspath(os.path.join(OUTPUT_DIR, "../../Example_Files/R/NADA2/ATS.R"))
    kenplot_path = os.path.abspath(os.path.join(OUTPUT_DIR, "../../Example_Files/R/NADA2/kenplot.R"))
    r.source(ats_script_path)
    r.source(kenplot_path)

    r("""
    library(NADA)
    # Helper to parse censored data
    # We need to manually parse because NADA doesn't have a 'RemoveAlphaDetect' equivalent built-in
    # conveniently exposed here, but we can use the python pre-processed columns if we pass them.
    """)

    # Use python pre-processing to get numeric/censored columns
    prep_df = mk.prepare_censored_data(df['value'])
    prep_df['t'] = df['t']

    # Convert 't' to numeric for ATS
    # ATS expects numeric X.
    # Use simple numeric time (0, 1, 2...) or ordinal date
    # MKS uses seconds for slope, but for comparison we should check what NADA does.
    # NADA ATS on numeric X returns slope in units of Y per unit of X.
    # To match MKS 'per second' output, we should pass seconds.
    prep_df['t_sec'] = prep_df['t'].astype('int64') // 10**9

    with localconverter(ro.default_converter + pandas2ri.converter):
        r_prep = ro.conversion.py2rpy(prep_df)

    r.assign('nada_data', r_prep)

    try:
        r("""
        # ATS(y.var, y.cen, x.var, LOG=FALSE)
        # Assuming prepare_censored_data returns 'value' (numeric) and 'censored' (bool)
        # cen_type: 'lt' is standard for NADA.

        # Note: NADA censoring indicator: TRUE = censored (detection limit).

        # ATS function in ATS.R expects:
        # ATS(y.var, y.cen, x.var, x.cen = rep(0, length(x.var)), LOG = TRUE, retrans = FALSE, ...)

        result <- ATS(nada_data$value, nada_data$censored, nada_data$t_sec, LOG=FALSE)
        """)

        result = r['result']
        # ATS returns a dataframe with intercept, slope, kendall_s, tau, pval
        slope = result.rx2('slope')[0]
        p = result.rx2('pval')[0]
        # ATS in NADA doesn't always return CIs in the main table easily without summary.
        # We'll set NaN for now unless we dig deeper into the object.
        lower_ci = np.nan
        upper_ci = np.nan

        return slope, p, lower_ci, upper_ci
    except Exception as e:
        print(f"R NADA Execution Failed: {e}")
        return np.nan, np.nan, np.nan, np.nan

def run_sensitivity_analysis(values, t, scenario):
    """
    Runs MKS with different lt_mult values to demonstrate sensitivity.
    """
    multipliers = [0.2, 0.5, 0.8]
    results = []

    prep_df = mk.prepare_censored_data(values)

    for mult in multipliers:
        # Use Standard MKS (nan method) but changing multipliers
        # Wait, if method='nan', ambiguous slopes are NaN.
        # But 'valid' slopes (between censored and uncensored) DO use the multiplier.
        # So changing multiplier SHOULD affect the slope even in 'nan' mode.
        res = mk.trend_test(prep_df, t,
                            lt_mult=mult,
                            sens_slope_method='nan',
                            slope_scaling='year')
        results.append({
            'lt_mult': mult,
            'slope': res.scaled_slope,
            'p_value': res.p
        })

    return results

def main():
    results_list = []

    scenarios = ['strong_increasing', 'weak_decreasing', 'stable']

    # Prepare README content
    readme_content = "# V-12: Sen's Slope Censored Multipliers\n\n"
    readme_content += "## Objective\n"
    readme_content += "Isolate and verify the effect of the `lt_mult` and `gt_mult` parameters. "
    readme_content += "The test uses data with **multiple censoring levels** (<1, <3, <5) to ensure "
    readme_content += "robust validation of multiplier application across different limits.\n\n"

    sensitivity_table = ""

    for scenario in scenarios:
        print(f"Running scenario: {scenario}")
        values, t = generate_sensitive_data(scenario)
        df = pd.DataFrame({'value': values, 't': t})

        # Pre-process for MKS
        mks_data = mk.prepare_censored_data(values)

        # 1. MKS Standard
        res_std = mk.trend_test(mks_data, t,
                                sens_slope_method='nan',
                                mk_test_method='robust',
                                slope_scaling='year')

        # Generate Plot for Strong Increasing
        if scenario == 'strong_increasing':
            mk.trend_test(mks_data, t,
                          sens_slope_method='nan',
                          mk_test_method='robust',
                          plot_path=PLOT_PATH)

        # 2. MKS LWP Mode
        res_lwp = mk.trend_test(mks_data, t,
                                sens_slope_method='lwp',
                                mk_test_method='lwp',
                                ci_method='lwp',
                                agg_method='lwp',
                                agg_period='month', # Data is monthly
                                slope_scaling='year')

        # 3. MKS ATS Mode
        res_ats = mk.trend_test(mks_data, t,
                                sens_slope_method='ats',
                                slope_scaling='year')

        # 4. R LWP
        r_lwp_slope, r_lwp_p, r_lwp_lci, r_lwp_uci = run_r_lwp(df)
        # R slopes are usually per year if data is monthly and correctly identified
        # We need to ensure we compare apples to apples.
        # MKS 'slope_scaling='year'' multiplies slope/sec by sec/year.
        # LWP R usually outputs slope/year.

        # 5. R NADA
        r_nada_slope, r_nada_p, r_nada_lci, r_nada_uci = run_r_nada(df)
        # NADA ATS on numeric seconds will return slope/second.
        # We need to scale it to year for comparison if MKS is scaled.
        if not np.isnan(r_nada_slope):
            r_nada_slope *= 31557600 # sec/year approx


        # Record Results
        row = {
            'test_id': f"V-12_{scenario}",
            'mk_py_slope': res_std.scaled_slope,
            'mk_py_p_value': res_std.p,
            'mk_py_lower_ci': res_std.lower_ci,
            'mk_py_upper_ci': res_std.upper_ci,

            'lwp_py_slope': res_lwp.scaled_slope,
            'lwp_py_p_value': res_lwp.p,
            'lwp_py_lower_ci': res_lwp.lower_ci,
            'lwp_py_upper_ci': res_lwp.upper_ci,

            'r_slope': r_lwp_slope,
            'r_p_value': r_lwp_p,
            'r_lower_ci': r_lwp_lci,
            'r_upper_ci': r_lwp_uci,

            'ats_py_slope': res_ats.scaled_slope,
            'ats_py_p_value': res_ats.p,
            'ats_py_lower_ci': res_ats.lower_ci,
            'ats_py_upper_ci': res_ats.upper_ci,

            'nada_r_slope': r_nada_slope,
            'nada_r_p_value': r_nada_p,
            'nada_r_lower_ci': r_nada_lci,
            'nada_r_upper_ci': r_nada_uci,
        }

        # Calculate Error vs R LWP
        if not np.isnan(r_lwp_slope) and r_lwp_slope != 0:
            row['slope_error'] = abs(row['lwp_py_slope'] - row['r_slope'])
            row['slope_pct_error'] = (row['slope_error'] / abs(row['r_slope'])) * 100
        else:
            row['slope_error'] = np.nan
            row['slope_pct_error'] = np.nan

        results_list.append(row)

        # Run Sensitivity Analysis for Weak Decreasing
        if scenario == 'weak_decreasing':
            sens_res = run_sensitivity_analysis(values, t, scenario)
            sensitivity_table += "\n### Multiplier Sensitivity (Weak Decreasing Scenario)\n"
            sensitivity_table += "Demonstrating the effect of changing `lt_mult` on the Sen's Slope.\n\n"
            sensitivity_table += "| lt_mult | Slope (units/year) | P-Value |\n"
            sensitivity_table += "| :--- | :--- | :--- |\n"
            for sr in sens_res:
                sensitivity_table += f"| {sr['lt_mult']} | {sr['slope']:.5f} | {sr['p_value']:.5f} |\n"

    # Save Master Results
    master_df = pd.DataFrame(results_list)
    if os.path.exists(MASTER_CSV_PATH):
        existing_df = pd.read_csv(MASTER_CSV_PATH)
        # Remove existing rows for these test_ids to avoid duplicates
        existing_df = existing_df[~existing_df['test_id'].str.startswith('V-12')]
        master_df = pd.concat([existing_df, master_df], ignore_index=True)
    master_df.to_csv(MASTER_CSV_PATH, index=False)

    # Create Long-Format Results Table for README
    # Columns: Test ID, Method, Slope, P-Value, Lower CI, Upper CI
    long_results = []

    current_results = master_df[master_df['test_id'].str.startswith('V-12')]

    for _, row in current_results.iterrows():
        # MannKenSen (Standard)
        long_results.append({
            'Test ID': row['test_id'],
            'Method': 'MannKenSen (Standard)',
            'Slope': row['mk_py_slope'],
            'P-Value': row['mk_py_p_value'],
            'Lower CI': row['mk_py_lower_ci'],
            'Upper CI': row['mk_py_upper_ci']
        })
        # MannKenSen (LWP Mode)
        long_results.append({
            'Test ID': row['test_id'],
            'Method': 'MannKenSen (LWP Mode)',
            'Slope': row['lwp_py_slope'],
            'P-Value': row['lwp_py_p_value'],
            'Lower CI': row['lwp_py_lower_ci'],
            'Upper CI': row['lwp_py_upper_ci']
        })
        # LWP-TRENDS (R)
        long_results.append({
            'Test ID': row['test_id'],
            'Method': 'LWP-TRENDS (R)',
            'Slope': row['r_slope'],
            'P-Value': row['r_p_value'],
            'Lower CI': row['r_lower_ci'],
            'Upper CI': row['r_upper_ci']
        })
        # MannKenSen (ATS)
        long_results.append({
            'Test ID': row['test_id'],
            'Method': 'MannKenSen (ATS)',
            'Slope': row['ats_py_slope'],
            'P-Value': row['ats_py_p_value'],
            'Lower CI': row['ats_py_lower_ci'],
            'Upper CI': row['ats_py_upper_ci']
        })
        # NADA2 (R)
        long_results.append({
            'Test ID': row['test_id'],
            'Method': 'NADA2 (R)',
            'Slope': row['nada_r_slope'],
            'P-Value': row['nada_r_p_value'],
            'Lower CI': row['nada_r_lower_ci'],
            'Upper CI': row['nada_r_upper_ci']
        })

    long_df = pd.DataFrame(long_results)

    # Create Accuracy Table
    accuracy_df = current_results[['test_id', 'slope_error', 'slope_pct_error']].copy()
    accuracy_df.columns = ['Test ID', 'Slope Error', 'Slope % Error']

    # Write README
    readme_content += "## Trend Plot (Strong Increasing)\n\n"
    readme_content += "![Trend Plot](plot_trend.png)\n\n"

    readme_content += "## Validation Results\n"
    readme_content += long_df.to_markdown(index=False, floatfmt=".5g")

    readme_content += "\n\n## LWP Accuracy (Python vs R)\n"
    readme_content += accuracy_df.to_markdown(index=False, floatfmt=".5g")

    readme_content += sensitivity_table

    with open(README_PATH, 'w') as f:
        f.write(readme_content)

    print(f"Validation complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
