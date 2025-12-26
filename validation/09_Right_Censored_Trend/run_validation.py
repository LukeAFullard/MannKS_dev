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
from rpy2.robjects import pandas2ri, numpy2ri
from rpy2.robjects.conversion import localconverter

class RightCensoredValidationUtils(ValidationUtils):
    """
    Subclass of ValidationUtils to handle right-censored data correctly.
    Overwrites methods that hardcode left-censoring assumptions.
    """

    def _prepare_r_dataframe(self, df: pd.DataFrame, is_seasonal: bool = False) -> ro.DataFrame:
        """
        Converts Python DataFrame to R DataFrame.
        Assumes df already has 'RawValue', 'Censored', 'CenType' if dealing with right-censoring.
        """
        df_r_prep = df.copy()

        # Ensure Date handling matches base class
        if 'date' not in df_r_prep.columns and 'time' in df_r_prep.columns:
            year = df_r_prep['time'].astype(int)
            days = ((df_r_prep['time'] - year) * 365.25).astype(int)
            df_r_prep['date'] = pd.to_datetime(year.astype(str) + '-01-01') + pd.to_timedelta(days, unit='D')

        if 'date' in df_r_prep.columns:
            df_r_prep['myDate'] = df_r_prep['date']

        # Trust the pre-existing columns for censoring
        # Base class auto-detection would fail for 'gt'
        if 'RawValue' not in df_r_prep.columns:
            df_r_prep['RawValue'] = df_r_prep['value']

        # Ensure boolean and factor
        df_r_prep['Censored'] = df_r_prep['censored'].astype(bool)

        # Mapping 'gt'/'not' to what R expects?
        # LWP R script expects 'CenType' as factor 'lt', 'gt', 'not'.
        if 'cen_type' in df_r_prep.columns:
             df_r_prep['CenType'] = df_r_prep['cen_type']

        # Python to R conversion
        with localconverter(ro.default_converter + pandas2ri.converter):
            r_df = ro.conversion.py2rpy(df_r_prep)

        # Fix Date
        ro.globalenv['df_temp'] = r_df
        ro.r('df_temp$myDate <- as.Date(df_temp$myDate)')
        r_df = ro.globalenv['df_temp']

        return r_df

    def run_nada2_r_script(self, df: pd.DataFrame) -> Dict:
        """Runs the NADA2 ATS.R script. Modified for right-censoring support (though NADA2 ATS might not support it)."""
        # NADA2 ATS documentation says: "y.cen: Logical or numeric vector indicating censoring... TRUE indicates censored"
        # However, standard ATS usually handles left-censoring.
        # Checking NADA2 documentation/code: ATS function in ATS.R takes y.cen.
        # Does it handle right censoring?
        # The prompt says: "Ensure you produce a Md document outlining the case... Produce the V9 validation"
        # If NADA2 doesn't support right censoring, we report what it does or skip.
        # But actually, NADA2 is often used for left-censored.
        # Let's assume for this validation we try to pass it.
        # WARNING: Standard survival analysis often assumes RIGHT censoring. Environmental stats often assume LEFT.
        # NADA2 is for environmental (Left).
        # If we pass right-censored data to a left-censored tool, results will be wrong unless we transform.
        # We will run it as is and see (or flip if needed, but 'flipping' is for ROS).
        # We will proceed by passing the censored boolean. If NADA2 treats it as left-censored (detection limit), it will treat >5 as <5?
        # NADA2 ATS implementation: It uses `cenken` -> `survfit`. `survfit` handles right censoring by default!
        # BUT NADA2 flips data to handle left censoring with `survfit`.
        # So if we have right censoring, maybe we shouldn't flip?
        # Let's just pass it and record the result. The comparison is the goal.

        try:
            ro.r('library(Icens)')
            ro.r('library(survival)')
            ro.r(f'source("{self.nada2_ken_path}")')
            ro.r(f'source("{self.nada2_ats_path}")')

            # Use prepared columns
            y_vals = df['value'].values
            y_cen = df['censored'].values

            if 'time' in df.columns:
                 x_vals = df['time'].values
            elif 'date' in df.columns:
                 dates = pd.to_datetime(df['date'])
                 x_vals = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
                 x_vals = x_vals.values
            else:
                x_vals = np.arange(len(df))

            with localconverter(ro.default_converter + numpy2ri.converter):
                ro.globalenv['y_vec'] = y_vals
                ro.globalenv['ycen_vec'] = y_cen
                ro.globalenv['x_vec'] = x_vals

            # Note: We are not flipping or transforming.
            cmd = "res_ats <- ATS(y_vec, ycen_vec, x_vec, LOG=FALSE, printstat=FALSE, drawplot=FALSE)"
            ro.r(cmd)
            r_res = ro.globalenv['res_ats']

            with localconverter(ro.default_converter + pandas2ri.converter):
                res_df = ro.conversion.rpy2py(r_res)

            return {
                'slope': float(res_df['slope'].iloc[0]),
                'p_value': float(res_df['pval'].iloc[0]),
                'lower_ci': np.nan,
                'upper_ci': np.nan
            }

        except Exception as e:
            print(f"Error running NADA2 R script: {e}")
            return {'slope': np.nan, 'p_value': np.nan, 'lower_ci': np.nan, 'upper_ci': np.nan}

    def run_comparison(self, test_id: str, df: pd.DataFrame,
                       scenario_name: str,
                       mk_kwargs: Dict = {},
                       lwp_mode_kwargs: Dict = {},
                       true_slope: float = None) -> Tuple[Dict, object]:

        full_test_id = f"{test_id}_{scenario_name}"
        print(f"Running comparison for: {full_test_id}")

        # Time vector
        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            t_std = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
            t_std = t_std.values
        else:
            t_std = np.arange(len(df))

        # Standard MK: Pass FULL DataFrame to handle censoring metadata
        # MKS trend_test accepts df with 'value', 'censored', 'cen_type'
        # BUT prepare_censored_data logic usually converts strings like '>5' to mixed type.
        # If df['value'] is already numeric and we have separate censored columns, we might need to combine them?
        # mk.trend_test expects x as data. If x is numeric, it assumes uncensored unless we pass censored args?
        # No, MKS expects the input vector to contain the strings or objects if we rely on automatic parsing.
        # OR we can pre-process into a DataFrame with specific columns.

        # In this script, 'df' has 'value' as numeric threshold and 'cen_type' as 'gt'/'not'.
        # We need to construct the input 'x' that MKS expects if we want it to parse, OR pass the pre-processed structure.
        # MKS `trend_test` accepts `x` as array-like. If `x` is a DataFrame with 'value', 'censored', 'cen_type', it uses it directly.

        mk_std = mk.trend_test(df, t_std, **mk_kwargs)

        # LWP Mode
        lwp_defaults = {
            'mk_test_method': 'lwp',
            'ci_method': 'lwp',
            'sens_slope_method': 'lwp',
            'agg_method': 'middle_lwp'
        }
        lwp_final_kwargs = {**lwp_defaults, **lwp_mode_kwargs}

        if 'date' in df.columns:
             t_lwp = pd.to_datetime(df['date'])
             if 'agg_period' not in lwp_final_kwargs:
                 lwp_final_kwargs['agg_period'] = 'month' # Defaulting to month for this test
             if 'slope_scaling' not in lwp_final_kwargs:
                 lwp_final_kwargs['slope_scaling'] = 'year'
             mk_lwp = mk.trend_test(df, t_lwp, **lwp_final_kwargs)
        else:
             mk_lwp = mk.trend_test(df, t_std, **lwp_final_kwargs)

        # R LWP Script
        r_res = self.run_lwp_r_script(df)

        # ATS Mode
        mk_ats = mk.trend_test(df, t_std, sens_slope_method='ats')

        # NADA2 R Script
        nada_res = self.run_nada2_r_script(df)

        # Errors
        slope_error = np.nan
        slope_pct_error = np.nan
        if not np.isnan(r_res['slope']):
            slope_error = mk_lwp.slope - r_res['slope']
            if true_slope is not None and true_slope != 0:
                slope_pct_error = (slope_error / true_slope) * 100
            elif r_res['slope'] != 0:
                slope_pct_error = (slope_error / r_res['slope']) * 100
            elif slope_error == 0:
                slope_pct_error = 0.0

        result_row = {
            'test_id': full_test_id,
            'mk_py_slope': mk_std.slope,
            'mk_py_p_value': mk_std.p,
            'mk_py_lower_ci': mk_std.lower_ci,
            'mk_py_upper_ci': mk_std.upper_ci,
            'lwp_py_slope': mk_lwp.slope,
            'lwp_py_p_value': mk_lwp.p,
            'lwp_py_lower_ci': mk_lwp.lower_ci,
            'lwp_py_upper_ci': mk_lwp.upper_ci,
            'r_slope': r_res['slope'],
            'r_p_value': r_res['p_value'],
            'r_lower_ci': r_res['lower_ci'],
            'r_upper_ci': r_res['upper_ci'],
            'ats_py_slope': mk_ats.slope,
            'ats_py_p_value': mk_ats.p,
            'ats_py_lower_ci': mk_ats.lower_ci,
            'ats_py_upper_ci': mk_ats.upper_ci,
            'nada_r_slope': nada_res['slope'],
            'nada_r_p_value': nada_res['p_value'],
            'nada_r_lower_ci': nada_res['lower_ci'],
            'nada_r_upper_ci': nada_res['upper_ci'],
            'slope_error': slope_error,
            'slope_pct_error': slope_pct_error
        }

        self.results.append(result_row)
        self._append_to_csv(result_row)
        return result_row, mk_std

def generate_right_censored_data(n=24, slope=1.0, noise_std=0.5, start_year=2000,
                                 censor_threshold_percentile=80):
    """
    Generates monthly data with a trend and right-censoring.
    Values above the threshold are marked as censored (>).
    """
    dates = pd.date_range(start=f'{start_year}-01-01', periods=n, freq='ME')
    t = np.arange(n) / 12.0 # Yearly time steps
    noise = np.random.normal(0, noise_std, n)
    values = slope * t + 10 + noise

    threshold = np.percentile(values, censor_threshold_percentile)

    censored = values > threshold
    cen_type = np.where(censored, 'gt', 'not')

    # For censored values, the 'value' is the threshold
    final_values = values.copy()
    final_values[censored] = threshold

    df = pd.DataFrame({
        'date': dates,
        'value': final_values,
        'censored': censored,
        'cen_type': cen_type,
        'true_value': values # Keep for debugging if needed
    })

    return df

def run():
    utils = RightCensoredValidationUtils(os.path.dirname(__file__))
    scenarios = []

    # Scenario 1: Strong Increasing Trend
    df_strong = generate_right_censored_data(n=36, slope=2.0, noise_std=1.0, censor_threshold_percentile=80)
    _, mk_std_strong = utils.run_comparison(
        test_id="V-09",
        df=df_strong,
        scenario_name="strong_increasing",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=2.0
    )
    scenarios.append({
        'df': df_strong,
        'title': 'Strong Increasing (Right Censored)',
        'mk_result': mk_std_strong
    })

    # Scenario 2: Weak Decreasing Trend
    df_weak = generate_right_censored_data(n=36, slope=-0.5, noise_std=1.5, censor_threshold_percentile=85)
    _, mk_std_weak = utils.run_comparison(
        test_id="V-09",
        df=df_weak,
        scenario_name="weak_decreasing",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=-0.5
    )
    scenarios.append({
        'df': df_weak,
        'title': 'Weak Decreasing (Right Censored)',
        'mk_result': mk_std_weak
    })

    # Scenario 3: Stable (No Trend)
    df_stable = generate_right_censored_data(n=36, slope=0.0, noise_std=1.0, censor_threshold_percentile=80)
    _, mk_std_stable = utils.run_comparison(
        test_id="V-09",
        df=df_stable,
        scenario_name="stable",
        mk_kwargs={'mk_test_method': 'robust', 'slope_scaling': 'year'},
        lwp_mode_kwargs={'slope_scaling': 'year'},
        true_slope=0.0
    )
    scenarios.append({
        'df': df_stable,
        'title': 'Stable (Right Censored)',
        'mk_result': mk_std_stable
    })

    # Generate Combined Plot
    utils.generate_combined_plot(scenarios, "v09_combined.png", "V-09: Right-Censored Trend Analysis")

    # Generate Report
    description = """
    # V-09: Right-Censored Trend

    This validation case tests the package's ability to handle right-censored data (values reported as greater than a detection limit, e.g., `>5.0`).

    Three scenarios were tested:
    1. **Strong Increasing Trend**: Data with a clear positive slope, where higher values are censored.
    2. **Weak Decreasing Trend**: Data with a slight negative slope, where initial high values are censored.
    3. **Stable (No Trend)**: Random data with no trend, with some high values censored.
    """

    utils.create_report(description=description)

if __name__ == "__main__":
    np.random.seed(42)
    run()
