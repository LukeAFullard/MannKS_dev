import streamlit as st
import pandas as pd
from modules.data_loader import load_data_ui
from modules.data_generator import generate_data_ui
from modules.settings import render_settings_ui
from modules.analysis import run_analysis
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

def main():
    # Sidebar Logo
    st.sidebar.image(LOGO_URL, use_container_width=True)
    st.sidebar.markdown("---")

    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(LOGO_URL, width=200)
    with col2:
        st.title("MannKenSen Analysis Tool")
        st.markdown("""
        Perform robust non-parametric trend analysis on unequally spaced time series with censored data.
        """)

    # Initialize Session State
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'history' not in st.session_state:
        st.session_state.history = []

    # --- Tabs ---
    tab_data, tab_inspect, tab_settings, tab_run, tab_results = st.tabs([
        "1. Data", "2. Data Inspection", "3. Configure Settings", "4. Run Analysis", "5. Results & Report"
    ])

    # --- 1. Data Tab ---
    with tab_data:
        data_source = st.radio("Choose Data Source", ["Upload File", "Generate Synthetic Data"], horizontal=True)

        if data_source == "Upload File":
            df = load_data_ui()
        else:
            df = generate_data_ui()

        if df is not None:
            st.session_state.data = df

        if st.session_state.data is not None:
            st.info(f"Current Data: {len(st.session_state.data)} observations loaded.")

            # Download processed data
            csv = st.session_state.data.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Processed CSV",
                csv,
                "processed_data.csv",
                "text/csv",
                key='download-csv'
            )

            with st.expander("View Data"):
                st.dataframe(st.session_state.data)

    # --- 2. Data Inspection Tab ---
    with tab_inspect:
        st.header("Data Inspection")
        if st.session_state.data is None:
            st.warning("Please load data first.")
        else:
            st.markdown("Assess data availability and suitable time increments.")

            col1, col2 = st.columns(2)
            with col1:
                prop_year_tol = st.slider("Min Prop. Years with Data", 0.1, 1.0, 0.8)
            with col2:
                prop_incr_tol = st.slider("Min Prop. Increments with Data", 0.1, 1.0, 0.8)

            if st.button("Inspect Data"):
                try:
                    # Prepare data for inspection (needs 'value' and 't' columns, 't' must be datetime)
                    inspect_df = st.session_state.data.copy()

                    # Convert t_original to datetime if it's not already
                    inspect_df['t'] = pd.to_datetime(inspect_df['t_original'])

                    # Create a temporary file for the plot
                    import tempfile
                    import os
                    tf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    plot_path = tf.name
                    tf.close()

                    result = inspect_trend_data(
                        inspect_df,
                        value_col='value',
                        time_col='t',
                        prop_year_tol=prop_year_tol,
                        prop_incr_tol=prop_incr_tol,
                        return_summary=True,
                        plot=True,
                        plot_path=plot_path
                    )

                    st.success("Inspection Complete")

                    st.subheader("Data Availability Summary")
                    st.dataframe(result.summary)

                    best = result.summary.loc[result.summary['data_ok'] == True]
                    if not best.empty:
                        best_inc = best.iloc[0]['increment']
                        st.info(f"Recommended Time Increment: **{best_inc}**")
                    else:
                        st.warning("No time increment met the specified tolerances.")

                    st.subheader("Inspection Plots")
                    st.image(plot_path)
                    os.remove(plot_path)

                except Exception as e:
                    st.error(f"Error during inspection: {str(e)}")


    # --- 3. Settings Tab ---
    with tab_settings:
        # Returns a dict of settings for all tests
        all_settings = render_settings_ui()
        st.session_state.settings = all_settings

    # --- 3. Run Analysis Tab ---
    with tab_run:
        st.header("Execute Analysis")

        if st.session_state.data is None:
            st.warning("Please load or generate data in the 'Data' tab first.")
        else:
            test_type = st.radio("Select Test to Run", ["Trend Test", "Seasonal Trend Test", "Seasonality Check"])

            # Show preview of settings for selected test
            if 'settings' in st.session_state:
                current_settings = st.session_state.settings.get(test_type.lower().replace(" ", "_"), {})
                st.markdown(f"**Current Settings for {test_type}:**")
                st.json(current_settings)

            if st.button("Run Analysis", type="primary"):
                with st.spinner("Running analysis..."):
                    # Get settings for this specific test
                    # keys in settings.py were: 'trend_test', 'seasonal_trend_test', 'check_seasonality'
                    key_map = {
                        "Trend Test": "trend_test",
                        "Seasonal Trend Test": "seasonal_trend_test",
                        "Seasonality Check": "check_seasonality"
                    }
                    settings_key = key_map[test_type]
                    params = st.session_state.settings.get(settings_key, {})

                    # Run
                    result = run_analysis(st.session_state.data, test_type, params)

                    # Store in history
                    st.session_state.history.append(result)

                    st.success("Analysis complete! Go to the 'Results & Report' tab to view details.")

    # --- 4. Results & Report Tab ---
    with tab_results:
        st.header("Analysis History")

        if not st.session_state.history:
            st.info("No analysis run yet.")
        else:
            # Report Download Button
            report_html = generate_html_report(st.session_state.history)
            st.download_button(
                label="Download Full HTML Report",
                data=report_html,
                file_name="mannkensen_report.html",
                mime="text/html"
            )

            st.markdown("---")

            # Display History (Reverse order to show newest first)
            for i, res in enumerate(reversed(st.session_state.history)):
                idx = len(st.session_state.history) - i
                with st.expander(f"Run {idx}: {res['test_type']} ({res['timestamp']})", expanded=(i==0)):

                    if res.get('error'):
                        st.error(f"Error: {res['error']}")
                        if 'traceback' in res:
                            st.code(res['traceback'])
                    else:
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

            if st.button("Clear History"):
                st.session_state.history = []
                st.rerun()

if __name__ == "__main__":
    main()
