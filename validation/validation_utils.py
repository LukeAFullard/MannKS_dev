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

        # Handle Missing Date if Time (Numeric Year) is present
        if 'date' not in df_r_prep.columns and 'time' in df_r_prep.columns:
            # Construct a fake date from decimal year for R script compatibility
            year = df_r_prep['time'].astype(int)
            days = ((df_r_prep['time'] - year) * 365.25).astype(int)
            # Use 'D' for days. ensure year is string for to_datetime
            df_r_prep['date'] = pd.to_datetime(year.astype(str) + '-01-01') + pd.to_timedelta(days, unit='D')

        # Ensure 'MyDate' exists (LWP script expects 'myDate')
        if 'date' in df_r_prep.columns:
            df_r_prep['myDate'] = df_r_prep['date']

        # Add LWP required columns if not present
        if 'RawValue' not in df_r_prep.columns:
            # Need to parse censoring
            if df_r_prep['value'].dtype == object:
                # Handle both < and >
                df_r_prep['RawValue'] = df_r_prep['value'].astype(str).str.replace('<', '').str.replace('>', '').astype(float)

                # Determine CenType
                conditions = [
                    df_r_prep['value'].astype(str).str.contains('<'),
                    df_r_prep['value'].astype(str).str.contains('>')
                ]
                choices = ['lt', 'gt']
                df_r_prep['CenType'] = np.select(conditions, choices, default='not')
                df_r_prep['Censored'] = df_r_prep['CenType'] != 'not'
            else:
                df_r_prep['RawValue'] = df_r_prep['value']
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
            # If date was generated from time, year column should be correct.
            # But checking df['date'] might fail if df didn't have it originally.
            # Check r_df columns or reconstruct logic.
            # We know _prepare_r_dataframe adds 'date' if missing.

            # Simple heuristic: if 'time' is in df and it looks like years (e.g. 2000, 2001),
            # LWP should use Year.

            is_annual = True
            # Check repetition of years in R dataframe
            ro.r('year_counts <- table(df_r$Year)')
            max_counts = ro.r('max(year_counts)')[0]
            if max_counts > 1:
                is_annual = False

            if is_annual:
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

            if 'value' in df.columns and df['value'].dtype == object and (df['value'].str.contains('<').any() or df['value'].str.contains('>').any()):
                 y_vals = df['value'].astype(str).str.replace('<', '').str.replace('>', '').astype(float).values
                 # Logical OR on contains < or >
                 is_censored = df['value'].astype(str).str.contains('<') | df['value'].astype(str).str.contains('>')
                 y_cen = is_censored.values
            else:
                y_vals = df['value'].values
                y_cen = np.zeros(len(df), dtype=bool)

            # Determine x_vals (time)
            if 'time' in df.columns:
                 x_vals = df['time'].values
            elif 'date' in df.columns:
                 dates = pd.to_datetime(df['date'])
                 # Convert to decimal year
                 x_vals = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
                 x_vals = x_vals.values
            else:
                x_vals = np.arange(len(df))

            # Explicit conversion to R vectors to avoid numpy2ri context issues
            ro.globalenv['y_vec'] = ro.FloatVector(y_vals)
            # BoolVector in R is logical
            ro.globalenv['ycen_vec'] = ro.BoolVector(y_cen)
            ro.globalenv['x_vec'] = ro.FloatVector(x_vals)

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

        # Pre-process censored data for Python if needed
        x_std = df['value']
        if df['value'].dtype == object:
             try:
                 x_std = mk.prepare_censored_data(df['value'])
             except Exception as e:
                 print(f"Warning: automatic pre-processing failed: {e}")

        # Standard MK: Use converted numeric time (decimal years)
        if 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            t_std = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
            t_std = t_std.values
        else:
            t_std = np.arange(len(df))

        # Pass x_std (which might be the DataFrame from prepare_censored_data)
        mk_std = mk.trend_test(x_std, t_std, **mk_kwargs)

        # LWP Mode: Try to mimic R behavior.
        lwp_defaults = {
            'mk_test_method': 'lwp',
            'ci_method': 'lwp',
            'sens_slope_method': 'lwp',
            'agg_method': 'middle_lwp'
        }
        lwp_final_kwargs = {**lwp_defaults, **lwp_mode_kwargs}

        if 'date' in df.columns:
             t_lwp = pd.to_datetime(df['date'])
             n_years = len(t_lwp.dt.year.unique())
             n_obs = len(t_lwp)

             if 'agg_period' not in lwp_final_kwargs:
                 if n_years == n_obs:
                     lwp_final_kwargs['agg_period'] = 'year'
                 else:
                     lwp_final_kwargs['agg_period'] = 'month' # Assumption

             if 'slope_scaling' not in lwp_final_kwargs:
                 lwp_final_kwargs['slope_scaling'] = 'year'

             mk_lwp = mk.trend_test(x_std, t_lwp, **lwp_final_kwargs)
        else:
             mk_lwp = mk.trend_test(x_std, t_std, **lwp_final_kwargs)

        r_res = self.run_lwp_r_script(df)

        mk_ats = mk.trend_test(x_std, t_std, sens_slope_method='ats')

        nada_res = self.run_nada2_r_script(df)

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
            else:
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
        return result_row, mk_std

    def _append_to_csv(self, row: Dict):
        df = pd.DataFrame([row])
        cols = pd.read_csv(self.master_csv_path, nrows=0).columns.tolist()
        df = df[cols]
        df.to_csv(self.master_csv_path, mode='a', header=False, index=False)

    def _get_decimal_year(self, df: pd.DataFrame) -> np.ndarray:
        """Converts dataframe date column to decimal year, matching run_comparison logic."""
        if 'time' in df.columns:
            return df['time'].values
        elif 'date' in df.columns:
            dates = pd.to_datetime(df['date'])
            t = dates.dt.year + (dates.dt.dayofyear - 1) / 365.25
            return t.values
        else:
            return np.arange(len(df))

    def generate_plot(self, df: pd.DataFrame, title: str, filename: str, mk_result=None):
        """Generates a simple plot of the data, optionally with trend line and CIs."""
        plt.figure(figsize=(10, 6))

        if 'time' in df.columns:
            x_plot = df['time']
        elif 'date' in df.columns:
            x_plot = df['date']
        else:
            x_plot = np.arange(len(df))

        y_plot = df['value']

        plt.plot(x_plot, y_plot, 'o', color='black', label='Data')

        # Add Trend Line and CIs if provided
        if mk_result is not None and not np.isnan(mk_result.slope):
            t_numeric = self._get_decimal_year(df)

            # Calculate Trend Line: y = slope * t + intercept
            y_trend = mk_result.slope * t_numeric + mk_result.intercept

            plt.plot(x_plot, y_trend, '-', color='blue', label=f"Sen's Slope: {mk_result.slope:.4f}")

            # Calculate CIs (Approximation for visualization: pivot around median)
            t_med = np.median(t_numeric)
            y_med = np.median(y_plot)

            if not np.isnan(mk_result.lower_ci):
                y_lower = mk_result.lower_ci * (t_numeric - t_med) + y_med
                plt.plot(x_plot, y_lower, '--', color='blue', alpha=0.5, label=f'90% CI')

            if not np.isnan(mk_result.upper_ci):
                y_upper = mk_result.upper_ci * (t_numeric - t_med) + y_med
                plt.plot(x_plot, y_upper, '--', color='blue', alpha=0.5)

                # Shade the confidence interval
                if not np.isnan(mk_result.lower_ci):
                    plt.fill_between(x_plot, y_lower, y_upper, color='blue', alpha=0.1)

        plt.title(title)
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.legend(loc='best')
        plt.grid(True, linestyle=':', alpha=0.6)

        plot_path = os.path.join(self.output_dir, filename)
        plt.savefig(plot_path)
        plt.close()
        print(f"Plot saved to {plot_path}")

    def create_report(self, filename='README.md', description=None):
        """Creates a Markdown report with results and plots in long format."""
        report_path = os.path.join(self.output_dir, filename)

        with open(report_path, 'w') as f:
            f.write(f"# Validation Report\n\n")

            if description:
                f.write(description + "\n\n")

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
