import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Optional, Tuple, List, Union
from datetime import datetime

# Add repo root to path to ensure MannKenSen can be imported
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import MannKenSen as mk

# RPy2 imports
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri, numpy2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr

# No global activation of pandas2ri to avoid deprecation warnings

class ValidationUtils:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.lwp_script_path = os.path.join(repo_root, 'Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r')
        self.nada2_ats_path = os.path.join(repo_root, 'Example_Files/R/NADA2/ATS.R')
        self.nada2_ken_path = os.path.join(repo_root, 'Example_Files/R/NADA2/NADA_ken.R')
        self.master_csv_path = os.path.join(repo_root, 'validation/master_results.csv')
        self.results = [] # Store results for this session

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def _prepare_r_dataframe(self, df: pd.DataFrame, is_seasonal: bool = False) -> ro.DataFrame:
        """
        Converts Python DataFrame to R DataFrame and adds necessary columns for LWP script.
        """
        df_r_prep = df.copy()

        # Ensure 'MyDate' exists (LWP script expects 'myDate')
        if 'date' in df_r_prep.columns:
            df_r_prep['myDate'] = df_r_prep['date']

        # Add LWP required columns if not present
        if 'RawValue' not in df_r_prep.columns:
            df_r_prep['RawValue'] = df_r_prep['value']

        if 'Censored' not in df_r_prep.columns:
            if df_r_prep['value'].dtype == object:
                df_r_prep['Censored'] = df_r_prep['value'].astype(str).str.contains('<')
                df_r_prep['RawValue'] = df_r_prep['value'].astype(str).str.replace('<', '').astype(float)
                df_r_prep['CenType'] = np.where(df_r_prep['Censored'], 'lt', 'not')
            else:
                df_r_prep['Censored'] = False
                df_r_prep['CenType'] = 'not'

        df_r_prep['Censored'] = df_r_prep['Censored'].astype(bool)

        with localconverter(ro.default_converter + pandas2ri.converter):
            r_df = ro.conversion.py2rpy(df_r_prep)

        # FORCE Date conversion: LWP expects 'Date' (days), but rpy2 passes POSIXct (seconds).
        # This causes slope calculation error by factor of 86400.
        ro.globalenv['df_temp'] = r_df
        ro.r('df_temp$myDate <- as.Date(df_temp$myDate)')
        r_df = ro.globalenv['df_temp']

        return r_df

    def run_lwp_r_script(self, df: pd.DataFrame, seasonal: bool = False) -> Dict:
        """Runs the LWP-TRENDS R script."""
        try:
            ro.r(f'source("{self.lwp_script_path}")')

            r_df = self._prepare_r_dataframe(df)

            # Inject dataframe into R environment
            ro.globalenv['df_r'] = r_df
            ro.r('df_r$CenType <- as.factor(df_r$CenType)')

            # Critical Step: Run GetMoreDateInfo to populate MidTimeIncrList and date columns
            ro.r('df_r <- GetMoreDateInfo(df_r)')

            # Set TimeIncr explicitly.
            # If unique years == count, assume annual. Otherwise assume monthly (use Month).
            if len(df['date'].dt.year.unique()) == len(df):
                 ro.r('df_r$TimeIncr <- df_r$Year')
            else:
                 ro.r('df_r$TimeIncr <- df_r$Month')

            if not seasonal:
                # Capture output
                cmd = """
                suppressWarnings(
                    result <- NonSeasonalTrendAnalysis(df_r, do.plot=FALSE, TimeIncrMed=TRUE, UseMidObs=TRUE)
                )
                """
                ro.r(cmd)

                if 'result' not in ro.globalenv:
                    return {'slope': np.nan, 'p_value': np.nan, 'lower_ci': np.nan, 'upper_ci': np.nan}

                r_result = ro.globalenv['result']

                if r_result == ro.r('NULL'):
                     return {'slope': np.nan, 'p_value': np.nan, 'lower_ci': np.nan, 'upper_ci': np.nan}

                with localconverter(ro.default_converter + pandas2ri.converter):
                    res_df = ro.conversion.rpy2py(r_result)

                if res_df is None or len(res_df) == 0:
                    return {'slope': np.nan, 'p_value': np.nan, 'lower_ci': np.nan, 'upper_ci': np.nan}

                return {
                    'slope': float(res_df['AnnualSenSlope'].iloc[0]),
                    'p_value': float(res_df['p'].iloc[0]),
                    'lower_ci': float(res_df['Sen_Lci'].iloc[0]),
                    'upper_ci': float(res_df['Sen_Uci'].iloc[0])
                }
            else:
                return {'slope': np.nan, 'p_value': np.nan, 'lower_ci': np.nan, 'upper_ci': np.nan}

        except Exception as e:
            print(f"Error running LWP R script: {e}")
            return {'slope': np.nan, 'p_value': np.nan, 'lower_ci': np.nan, 'upper_ci': np.nan}

    def run_nada2_r_script(self, df: pd.DataFrame) -> Dict:
        """Runs the NADA2 ATS.R script."""
        try:
            # Load required packages explicitly
            ro.r('library(Icens)')
            ro.r('library(survival)')

            ro.r(f'source("{self.nada2_ken_path}")')
            ro.r(f'source("{self.nada2_ats_path}")')

            if 'value' in df.columns and df['value'].dtype == object and df['value'].str.contains('<').any():
                 y_vals = df['value'].astype(str).str.replace('<', '').astype(float).values
                 y_cen = df['value'].astype(str).str.contains('<').values
            else:
                y_vals = df['value'].values
                y_cen = np.zeros(len(df), dtype=bool)

            if 'date' in df.columns:
                 dates = pd.to_datetime(df['date'])
                 # Convert to decimal year
                 x_vals = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
                 x_vals = x_vals.values
            else:
                x_vals = np.arange(len(df))

            with localconverter(ro.default_converter + numpy2ri.converter):
                ro.globalenv['y_vec'] = y_vals
                ro.globalenv['ycen_vec'] = y_cen
                ro.globalenv['x_vec'] = x_vals

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
                       lwp_mode_kwargs: Dict = {}) -> Dict:

        full_test_id = f"{test_id}_{scenario_name}"
        print(f"Running comparison for: {full_test_id}")

        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            t = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
            t = t.values
        else:
            t = np.arange(len(df))

        mk_std = mk.trend_test(df['value'], t, **mk_kwargs)

        lwp_defaults = {
            'mk_test_method': 'lwp',
            'ci_method': 'lwp',
            'sens_slope_method': 'lwp',
            'agg_method': 'middle_lwp'
        }
        lwp_final_kwargs = {**lwp_defaults, **lwp_mode_kwargs}

        mk_lwp = mk.trend_test(df['value'], t, **lwp_final_kwargs)

        r_res = self.run_lwp_r_script(df)

        mk_ats = mk.trend_test(df['value'], t, sens_slope_method='ats')

        nada_res = self.run_nada2_r_script(df)

        if not np.isnan(r_res['slope']) and r_res['slope'] != 0:
            slope_error = mk_lwp.slope - r_res['slope']
            slope_pct_error = (slope_error / r_res['slope']) * 100
        elif r_res['slope'] == 0:
             slope_error = mk_lwp.slope
             slope_pct_error = 0.0
        else:
             slope_error = np.nan
             slope_pct_error = np.nan

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
        return result_row

    def _append_to_csv(self, row: Dict):
        df = pd.DataFrame([row])
        cols = pd.read_csv(self.master_csv_path, nrows=0).columns.tolist()
        df = df[cols]
        df.to_csv(self.master_csv_path, mode='a', header=False, index=False)

    def generate_plot(self, df: pd.DataFrame, title: str, filename: str):
        """Generates a simple plot of the data."""
        plt.figure(figsize=(10, 6))

        if 'date' in df.columns:
            x = df['date']
        else:
            x = np.arange(len(df))

        y = df['value']

        plt.plot(x, y, 'o-', label='Data')

        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)

        plot_path = os.path.join(self.output_dir, filename)
        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved to {plot_path}")

    def create_report(self, filename='README.md'):
        """Creates a Markdown report with results and plots in long format."""
        report_path = os.path.join(self.output_dir, filename)

        with open(report_path, 'w') as f:
            f.write(f"# Validation Report\n\n")

            # Plots
            f.write("## Plots\n")
            plots = [p for p in os.listdir(self.output_dir) if p.endswith('.png')]
            for p in sorted(plots):
                f.write(f"### {p}\n")
                f.write(f"![{p}]({p})\n\n")

            # Results Table (Long Format)
            f.write("## Results\n")
            if self.results:
                long_rows = []
                for res in self.results:
                    test_id = res.get('test_id', 'Unknown')

                    # Define method mappings
                    methods = [
                        ('MannKenSen (Standard)', 'mk_py'),
                        ('MannKenSen (LWP Mode)', 'lwp_py'),
                        ('LWP-TRENDS (R)', 'r'),
                        ('MannKenSen (ATS)', 'ats_py'),
                        ('NADA2 (R)', 'nada_r')
                    ]

                    for method_name, prefix in methods:
                        row = {
                            'Test ID': test_id,
                            'Method': method_name,
                            'Slope': res.get(f'{prefix}_slope', np.nan),
                            'P-Value': res.get(f'{prefix}_p_value', np.nan),
                            'Lower CI': res.get(f'{prefix}_lower_ci', np.nan),
                            'Upper CI': res.get(f'{prefix}_upper_ci', np.nan)
                        }
                        long_rows.append(row)

                df_long = pd.DataFrame(long_rows)
                f.write(df_long.to_markdown(index=False))
                f.write("\n\n")

                # LWP Accuracy Table
                f.write("## LWP Accuracy (Python vs R)\n")
                accuracy_rows = []
                for res in self.results:
                    accuracy_rows.append({
                        'Test ID': res.get('test_id'),
                        'Slope Error': res.get('slope_error'),
                        'Slope % Error': res.get('slope_pct_error')
                    })
                df_acc = pd.DataFrame(accuracy_rows)
                f.write(df_acc.to_markdown(index=False))
                f.write("\n")

        print(f"Report saved to {report_path}")
