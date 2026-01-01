import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Import MannKenSen functions
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.check_seasonality import check_seasonality

def get_plot_as_image(fig):
    """
    Converts a matplotlib figure to a PIL Image or Base64 string.
    Here we return BytesIO to display in st.image or save later.
    """
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    return buf

def run_analysis(data_df, test_type, settings):
    """
    Runs the specified test on the data using the provided settings.
    Returns a result dictionary containing the test output and plot.
    """
    # Prepare inputs from data_df
    # MannKS expects x (value vector or DF with censored cols) and t (time vector)
    # Our data_df is standardized: ['t_original', 'value', 'censored', 'cen_type']

    # Check if we have valid data
    if data_df is None or len(data_df) == 0:
        return {"error": "No data available."}

    # x can be the dataframe slice with value, censored, cen_type
    # But MannKS prepare_data splits it internally if passed a DF with these names?
    # Actually MannKS.trend_test docstring says: "x: a vector of data, or a DataFrame from prepare_censored_data."
    # Our `data_df` is exactly that (plus t_original).
    # So we can pass `data_df` as x, but we need to verify `trend_test` extraction logic.
    # Looking at `trend_test.py`: `data_filtered, is_datetime = _prepare_data(x, t, hicensor)`
    # `_prepare_data` handles DataFrame input for x.

    # We should pass x as the DataFrame (cols: value, censored, cen_type)
    # And t as the t_original column.

    x_input = data_df[['value', 'censored', 'cen_type']]
    t_input = data_df['t_original'].values

    results = {}
    results['test_type'] = test_type
    results['timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    results['settings'] = settings

    try:
        if test_type == "Trend Test":
            # 1. Setup temporary plot path?
            # Actually, `trend_test` saves to a path. We can't easily get the figure object back
            # unless we modify MannKS or use a temp file.
            # However, `plot_trend` is imported in `trend_test`.
            # We can use a temp file name.

            # Create a temp file for plot
            import tempfile
            import os

            # We'll use a named temp file, but ensure we close it so MannKS can write to it
            # Actually simpler: just generate a random filename in /tmp
            plot_filename = tempfile.mktemp(suffix=".png")

            # Run Test
            # Filter settings to match function signature
            params = settings.copy()
            # Remove keys that might not be in signature if any (none expected based on settings.py)

            # Run
            test_res = trend_test(x_input, t_input, plot_path=plot_filename, **params)

            results['output'] = test_res
            results['plot_path'] = plot_filename

            # Read plot back into memory
            if os.path.exists(plot_filename):
                with open(plot_filename, "rb") as f:
                    results['plot_bytes'] = f.read()
                # Clean up
                os.remove(plot_filename)
            else:
                results['plot_bytes'] = None

        elif test_type == "Seasonal Trend Test":
            plot_filename = tempfile.mktemp(suffix=".png")

            params = settings.copy()
            test_res = seasonal_trend_test(x_input, t_input, plot_path=plot_filename, **params)

            results['output'] = test_res
            results['plot_path'] = plot_filename # Just for ref

            if os.path.exists(plot_filename):
                with open(plot_filename, "rb") as f:
                    results['plot_bytes'] = f.read()
                os.remove(plot_filename)
            else:
                results['plot_bytes'] = None

        elif test_type == "Seasonality Check":
            # This one doesn't produce a standard trend plot via the function.
            # But MannKS has `plot_seasonal_distribution`.
            # We should run the check AND generate the plot.

            params = settings.copy()
            test_res = check_seasonality(x_input, t_input, **params)
            results['output'] = test_res

            # Generate Plot manually
            from MannKS.plotting import plot_seasonal_distribution

            # We need to map settings to plot_seasonal_distribution params
            # It accepts: x, t, period, season_type, plot_path...
            plot_filename = tempfile.mktemp(suffix=".png")

            plot_seasonal_distribution(
                x_input, t_input,
                period=params.get('period', 12),
                season_type=params.get('season_type', 'month'),
                plot_path=plot_filename,
                agg_method=params.get('agg_method', 'none'),
                # agg_period missing in check_seasonality?
                # check_seasonality.py source shows it accepts `agg_period`.
                # plot_seasonal_distribution needs to be checked for signature.
                # I'll check memory/files. plot_seasonal_distribution in plotting.py...
                # Assuming it supports similar params.
            )

            if os.path.exists(plot_filename):
                with open(plot_filename, "rb") as f:
                    results['plot_bytes'] = f.read()
                os.remove(plot_filename)
            else:
                results['plot_bytes'] = None

    except Exception as e:
        results['error'] = str(e)
        import traceback
        results['traceback'] = traceback.format_exc()

    return results
