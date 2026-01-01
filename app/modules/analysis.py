import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import tempfile
import os

# Import MannKenSen functions
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.check_seasonality import check_seasonality
from MannKS.plotting import plot_seasonal_distribution

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

    if data_df is None or len(data_df) == 0:
        return {"error": "No data available."}

    x_input = data_df[['value', 'censored', 'cen_type']]
    t_input = data_df['t_original'].values

    results = {}
    results['test_type'] = test_type
    results['timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    results['settings'] = settings

    # Secure temporary file creation helper
    def create_temp_plot_file():
        tf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tf.close()
        return tf.name

    try:
        if test_type == "Trend Test":
            # Use BytesIO for in-memory plotting
            plot_buffer = BytesIO()

            # Run Test
            params = settings.copy()
            test_res = trend_test(x_input, t_input, plot_path=plot_buffer, **params)

            results['output'] = test_res
            # We don't store a path anymore, but we can store a fake name if needed by something else
            results['plot_path'] = "memory.png"
            results['plot_bytes'] = plot_buffer.getvalue()


        elif test_type == "Seasonal Trend Test":
            plot_buffer = BytesIO()

            params = settings.copy()
            test_res = seasonal_trend_test(x_input, t_input, plot_path=plot_buffer, **params)

            results['output'] = test_res
            results['plot_path'] = "memory.png"
            results['plot_bytes'] = plot_buffer.getvalue()


        elif test_type == "Seasonality Check":
            params = settings.copy()
            test_res = check_seasonality(x_input, t_input, **params)
            results['output'] = test_res

            # Generate Plot manually
            plot_buffer = BytesIO()

            # plot_seasonal_distribution does not support agg_method or agg_period
            # We must pass only the supported arguments.
            # It accepts: x, t, period, season_type, plot_path

            plot_seasonal_distribution(
                x_input['value'],
                t_input,
                period=params.get('period', 12),
                season_type=params.get('season_type', 'month'),
                plot_path=plot_buffer
            )

            results['plot_bytes'] = plot_buffer.getvalue()

    except Exception as e:
        results['error'] = str(e)
        import traceback
        results['traceback'] = traceback.format_exc()

    return results
