import streamlit as st
import pandas as pd
from modules.data_loader import load_data_ui
from modules.data_generator import generate_data_ui
from modules.settings import render_settings_ui
from modules.analysis import run_analysis
from modules.workflow import run_auto_analysis
from modules.reporting import generate_html_report
from MannKS.inspection import inspect_trend_data

# Set page config
st.set_page_config(page_title="MannKenSen Analysis App", layout="wide", page_icon="📈")

import os

def inject_custom_css():
    """Inject modern, sleek CSS into the Streamlit app"""
    css_file = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

inject_custom_css()

LOGO_URL = "https://raw.githubusercontent.com/LukeAFullard/MannKS/main/assets/logo.png"

def display_results(history_item):
    """Reusable component to display analysis results."""
    res = history_item

    if res.get('error'):
        st.error(f"Error: {res['error']}")
        return

    # Special handling for Auto-Analysis composite result
    if 'seasonality_result' in res and 'trend_result' in res:
        # Show Seasonality Check
        seas = res['seasonality_result']
        trend = res['trend_result']

        st.info(f"**Automatic Analysis Report**")

        col1, col2 = st.columns(2)
        with col1:
             st.markdown("#### 1. Seasonality Check")
             st.write(f"Result: **{'Seasonal' if seas.is_seasonal else 'Not Seasonal'}** (P={seas.p_value:.4f})")
             if seas.is_seasonal:
                 st.caption("Seasonality detected. Running Seasonal Mann-Kendall Test.")
             else:
                 st.caption("No significant seasonality. Running Standard Mann-Kendall Test.")

        with col2:
            st.markdown(f"#### 2. {res['test_type']}")
            st.metric("Trend", trend.classification)
            st.write(f"**P-value:** {trend.p:.4f}")
            st.write(f"**Slope:** {trend.scaled_slope:.4g} {trend.slope_units}")
            st.write(f"**Confidence:** {trend.C:.4f}")
            if trend.analysis_notes:
                st.warning(f"Notes: {', '.join(trend.analysis_notes)}")

        if res.get('plot_bytes'):
            st.image(res['plot_bytes'], use_container_width=True)

    else:
        # Standard Single Test Result
        output = res['output']
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Statistics")
            if hasattr(output, 'trend'): # Trend / Seasonal Trend
                st.metric("Trend", output.classification)
                st.write(f"**P-value:** {output.p:.4f}")
                st.write(f"**Slope:** {output.scaled_slope:.4g} {output.slope_units}")
                st.write(f"**Kendall's Tau:** {output.Tau:.4f}")
                st.write(f"**Confidence:** {output.C:.4f}")
                if output.analysis_notes:
                    st.warning(f"Notes: {', '.join(output.analysis_notes)}")

            elif hasattr(output, 'is_seasonal'): # Seasonality Check
                st.metric("Seasonal?", "Yes" if output.is_seasonal else "No")
                st.write(f"**H-Statistic:** {output.h_statistic:.4f}")
                st.write(f"**P-value:** {output.p_value:.4f}")

        with col2:
            if res.get('plot_bytes'):
                st.image(res['plot_bytes'], use_container_width=True)


def main():
    # Sidebar Logo
    st.sidebar.image(LOGO_URL, use_container_width=True)
    st.sidebar.markdown("---")

    # Global Sidebar Controls
    st.sidebar.header("Global Controls")
    advanced_mode = st.sidebar.toggle("Advanced Mode", False)

    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(LOGO_URL, width=200)
    with col2:
        st.title("MannKenSen Analysis Tool")

    # Initialize Session State
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'last_result' not in st.session_state:
        st.session_state.last_result = None

    # --- Main Navigation ---
    tab_welcome, tab_dashboard, tab_report = st.tabs(["👋 Welcome", "📊 Analysis Dashboard", "📜 Full Report"])

    # --- 1. Welcome Tab ---
    with tab_welcome:
        welcome_file = os.path.join(os.path.dirname(__file__), "welcome.md")
        if os.path.exists(welcome_file):
            with open(welcome_file, "r") as f:
                st.markdown(f.read())
        else:
            st.markdown("Welcome to the MannKenSen Analysis Tool.")

    # --- 2. Dashboard Tab ---
    with tab_dashboard:
        # A. Data Loading Section
        st.markdown("### 1. Load Data")
        with st.container():
            col_d1, col_d2 = st.columns([1, 2])
            with col_d1:
                data_source = st.radio("Source", ["Upload File", "Generate Synthetic"], horizontal=True)

            with col_d2:
                if data_source == "Upload File":
                    df = load_data_ui()
                else:
                    df = generate_data_ui()

            if df is not None:
                st.session_state.data = df
                st.success(f"Loaded {len(df)} observations.")

            # Data Preview Expander
            if st.session_state.data is not None:
                with st.expander("View & Download Data"):
                    csv = st.session_state.data.to_csv(index=False).encode('utf-8')
                    st.download_button("Download CSV", csv, "data.csv", "text/csv")
                    st.dataframe(st.session_state.data, height=200)

        st.markdown("---")

        # B. Analysis Controls
        st.markdown("### 2. Run Analysis")

        if st.session_state.data is None:
            st.info("Please load data above to proceed.")
        else:
            if not advanced_mode:
                # --- SIMPLE MODE ---
                st.info("Simple Mode: Automatically checks for seasonality and runs the appropriate trend test.")

                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    sim_alpha = st.number_input("Significance Level (alpha)", 0.001, 0.5, 0.05, help="Standard is 0.05 (95% confidence)")
                with col_s2:
                    sim_period = st.number_input("Seasonal Period", min_value=2, value=12, help="e.g., 12 for monthly data")
                with col_s3:
                    sim_season_type = st.selectbox("Season Type", ['month', 'quarter', 'day_of_week', 'day_of_year', 'year'], help="Unit of the seasonal cycle")

                if st.button("Run Auto-Analysis", type="primary"):
                    with st.spinner("Running intelligent analysis..."):
                        res = run_auto_analysis(st.session_state.data, sim_alpha, sim_period, sim_season_type)

                        # Add timestamp
                        res['timestamp'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                        res['settings'] = {'mode': 'auto', 'alpha': sim_alpha, 'period': sim_period}

                        st.session_state.last_result = res
                        st.session_state.history.append(res)

            else:
                # --- ADVANCED MODE ---
                st.warning("Advanced Mode: Manual control enabled.")

                # Render Settings
                all_settings = render_settings_ui()

                st.subheader("Execute Test")
                test_type = st.selectbox("Select Test", ["Trend Test", "Seasonal Trend Test", "Seasonality Check"])

                # Data Inspection Tool (Only in Advanced)
                if st.checkbox("Run Data Inspection Tool first?"):
                    st.caption("Inspect data availability and suitability.")
                    col_i1, col_i2 = st.columns(2)
                    with col_i1:
                        prop_year_tol = st.slider("Min Prop. Years", 0.1, 1.0, 0.8, key="adv_prop_year")
                    with col_i2:
                        prop_incr_tol = st.slider("Min Prop. Increments", 0.1, 1.0, 0.8, key="adv_prop_incr")

                    if st.button("Run Inspection"):
                         try:
                            # Reuse inspection logic
                            inspect_df = st.session_state.data.copy()
                            # Ensure time is datetime
                            if not pd.api.types.is_datetime64_any_dtype(inspect_df['t_original']):
                                 try:
                                     inspect_df['t'] = pd.to_datetime(inspect_df['t_original'])
                                 except:
                                     st.error("Time column must be convertible to datetime for inspection.")
                                     inspect_df = None
                            else:
                                inspect_df['t'] = inspect_df['t_original']

                            if inspect_df is not None:
                                from io import BytesIO
                                plot_buffer = BytesIO()

                                result = inspect_trend_data(
                                    inspect_df,
                                    value_col='value',
                                    time_col='t',
                                    prop_year_tol=prop_year_tol,
                                    prop_incr_tol=prop_incr_tol,
                                    return_summary=True,
                                    plot=True,
                                    plot_path=plot_buffer
                                )

                                st.success("Inspection Complete")
                                st.dataframe(result.summary)
                                st.image(plot_buffer.getvalue())

                         except Exception as e:
                             st.error(f"Inspection Error: {e}")

                if st.button(f"Run {test_type}", type="primary"):
                    with st.spinner("Running analysis..."):
                         key_map = {
                            "Trend Test": "trend_test",
                            "Seasonal Trend Test": "seasonal_trend_test",
                            "Seasonality Check": "check_seasonality"
                        }
                         settings_key = key_map[test_type]
                         params = all_settings.get(settings_key, {})

                         res = run_analysis(st.session_state.data, test_type, params)
                         st.session_state.last_result = res
                         st.session_state.history.append(res)


        # C. Immediate Results Display
        if st.session_state.last_result:
            st.markdown("---")
            st.markdown("### 3. Results")
            display_results(st.session_state.last_result)


    # --- 3. Report Tab ---
    with tab_report:
        st.header("Session History")
        if not st.session_state.history:
            st.info("No analysis run yet.")
        else:
            report_html = generate_html_report(st.session_state.history)
            st.download_button("Download Report", report_html, "report.html", "text/html")

            for i, res in enumerate(reversed(st.session_state.history)):
                idx = len(st.session_state.history) - i
                with st.expander(f"Run {idx}: {res.get('test_type', 'Auto Analysis')} @ {res.get('timestamp')}"):
                    display_results(res)

            if st.button("Clear History"):
                st.session_state.history = []
                st.session_state.last_result = None
                st.rerun()

if __name__ == "__main__":
    main()
