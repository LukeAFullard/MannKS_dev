import streamlit as st
import pandas as pd
from MannKS.check_seasonality import check_seasonality
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from io import BytesIO

def run_auto_analysis(data_df, alpha, period, season_type):
    """
    Automatically checks for seasonality and runs the appropriate trend test.

    Returns a dictionary with:
    - 'seasonality_result': Output from check_seasonality
    - 'trend_result': Output from the selected trend test
    - 'test_type': 'Seasonal Trend Test' or 'Trend Test'
    - 'plot_bytes': In-memory plot of the trend analysis
    - 'error': Error message if any
    """

    if data_df is None or len(data_df) == 0:
        return {"error": "No data available."}

    x_input = data_df[['value', 'censored', 'cen_type']]
    t_input = data_df['t_original'].values

    results = {}

    try:
        # 1. Run Seasonality Check
        # We need to map simple inputs to check_seasonality params
        # Note: Aggregation is 'none' by default for auto mode to keep it simple,
        # unless we want to enforce it for robustness?
        # Let's stick to simple defaults: no agg unless user sets it in advanced.

        seasonality_res = check_seasonality(
            x_input,
            t_input,
            alpha=alpha,
            period=period,
            season_type=season_type
        )

        results['seasonality_result'] = seasonality_res

        # 2. Decide on Test
        if seasonality_res.is_seasonal:
            test_type = "Seasonal Trend Test"
            # Run Seasonal Test
            plot_buffer = BytesIO()
            trend_res = seasonal_trend_test(
                x_input,
                t_input,
                alpha=alpha,
                period=period,
                season_type=season_type,
                plot_path=plot_buffer,
                mk_test_method='robust', # robust default
                sens_slope_method='nan', # safe default
                ci_method='direct',
                tau_method='b'
            )
            results['plot_bytes'] = plot_buffer.getvalue()

        else:
            test_type = "Trend Test"
            # Run Standard Trend Test
            plot_buffer = BytesIO()
            trend_res = trend_test(
                x_input,
                t_input,
                alpha=alpha,
                plot_path=plot_buffer,
                mk_test_method='robust',
                sens_slope_method='nan',
                ci_method='direct',
                tau_method='b'
            )
            results['plot_bytes'] = plot_buffer.getvalue()

        results['trend_result'] = trend_res
        results['test_type'] = test_type

    except Exception as e:
        import traceback
        results['error'] = f"{str(e)}\n\n{traceback.format_exc()}"

    return results
