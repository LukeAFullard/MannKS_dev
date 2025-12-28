
import os
import sys
import numpy as np
import pandas as pd
import MannKenSen as mk
from datetime import datetime, timedelta

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

try:
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri
    from rpy2.robjects.conversion import localconverter
except ImportError:
    ro = None

class ValidationUtils:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
        self.lwp_script_path = os.path.join(self.repo_root, 'Example_Files/R/LWPTrends_v2502/LWPTrends_v2502.r')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def run_lwp_r_script(self, df: pd.DataFrame, time_incr_col: str = 'Month') -> dict:
        if ro is None: return {'slope': np.nan, 'p_value': np.nan}
        try:
            ro.r(f'source("{self.lwp_script_path}")')

            # Prepare DataFrame for R
            df_r = df.copy()
            if 'date' in df_r.columns:
                df_r['myDate'] = pd.to_datetime(df_r['date'])

            # R expects Censored/CenType even if all false
            if 'censored' not in df_r.columns:
                df_r['Censored'] = False
            else:
                df_r['Censored'] = df_r['censored']

            if 'cen_type' not in df_r.columns:
                df_r['CenType'] = 'not'
            else:
                df_r['CenType'] = df_r['cen_type']

            df_r['RawValue'] = df_r['value']

            with localconverter(ro.default_converter + pandas2ri.converter):
                r_df = ro.conversion.py2rpy(df_r)

            ro.globalenv['df_temp'] = r_df
            ro.r('df_temp$myDate <- as.Date(df_temp$myDate)')
            # Important: GetMoreDateInfo is needed
            ro.r('df_temp <- GetMoreDateInfo(df_temp)')

            # Set TimeIncr for aggregation
            ro.r(f'df_temp$TimeIncr <- df_temp${time_incr_col}')

            # Run NonSeasonalTrendAnalysis
            cmd = """
            suppressWarnings(
                result <- NonSeasonalTrendAnalysis(df_temp, do.plot=FALSE, TimeIncrMed=TRUE, UseMidObs=TRUE)
            )
            """
            ro.r(cmd)

            if 'result' not in ro.globalenv or ro.globalenv['result'] == ro.r('NULL'):
                 return {'slope': np.nan, 'p_value': np.nan}

            with localconverter(ro.default_converter + pandas2ri.converter):
                res_df = ro.conversion.rpy2py(ro.globalenv['result'])

            return {
                'slope': float(res_df['AnnualSenSlope'].iloc[0]),
                'p_value': float(res_df['p'].iloc[0])
            }

        except Exception as e:
            print(f"R Error: {e}")
            return {'slope': np.nan, 'p_value': np.nan}

    def create_report(self, results):
        md = "# V-27: LWP Aggregation Verification\n\n"
        md += "Comparison of Python `agg_method='lwp'` vs R `UseMidObs=TRUE`.\n\n"

        headers = ["Scenario", "Metric", "Python (LWP)", "R", "Match"]
        rows = []

        for res in results:
            py = res['py']
            r = res['r']
            name = res['name']

            slope_match = "✅" if np.isclose(py.slope, r['slope'], atol=1e-4) else "❌"
            rows.append([name, "Slope", f"{py.slope:.5f}", f"{r['slope']:.5f}", slope_match])

            p_match = "✅" if np.isclose(py.p, r['p_value'], atol=1e-4) else "❌"
            rows.append([name, "P-Value", f"{py.p:.5f}", f"{r['p_value']:.5f}", p_match])

            rows.append(["---", "---", "---", "---", "---"])

        from tabulate import tabulate
        md += tabulate(rows, headers=headers, tablefmt="github")

        with open(os.path.join(self.output_dir, 'README.md'), 'w') as f:
            f.write(md)
        print("Report generated.")

def run():
    print("Running V-27: LWP Aggregation...")
    utils = ValidationUtils(os.path.dirname(__file__))

    # 1. Monthly Aggregation
    np.random.seed(42)
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2004, 12, 31)
    all_dates = pd.date_range(start_date, end_date, freq='D')
    sample_dates = np.random.choice(all_dates, 300, replace=False)
    sample_dates.sort()

    t = (sample_dates - np.datetime64('1970-01-01')).astype('timedelta64[D]').astype(int) / 365.25
    values = 2.0 * t + 10 + np.random.normal(0, 1.0, len(t))
    df_monthly = pd.DataFrame({'date': sample_dates, 'value': values})

    py_res_monthly = mk.trend_test(
        df_monthly['value'],
        df_monthly['date'],
        agg_method='lwp',
        agg_period='month',
        mk_test_method='lwp',
        ci_method='lwp',
        slope_scaling='year'
    )
    r_res_monthly = utils.run_lwp_r_script(df_monthly, 'Month')

    # 2. Quarterly Aggregation
    # Use same data but aggregate to Quarter
    py_res_qtr = mk.trend_test(
        df_monthly['value'],
        df_monthly['date'],
        agg_method='lwp',
        agg_period='quarter',
        mk_test_method='lwp',
        ci_method='lwp',
        slope_scaling='year'
    )
    r_res_qtr = utils.run_lwp_r_script(df_monthly, 'Qtr')

    results = [
        {'name': 'Monthly Aggregation', 'py': py_res_monthly, 'r': r_res_monthly},
        {'name': 'Quarterly Aggregation', 'py': py_res_qtr, 'r': r_res_qtr}
    ]
    utils.create_report(results)

if __name__ == "__main__":
    run()
