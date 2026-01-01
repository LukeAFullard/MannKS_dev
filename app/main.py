import streamlit as st
import pandas as pd
from app.modules.data_loader import load_data_ui
from app.modules.data_generator import generate_data_ui
from app.modules.settings import render_settings_ui
from app.modules.analysis import run_analysis
from app.modules.reporting import generate_html_report

# Set page config
st.set_page_config(page_title="MannKenSen Analysis App", layout="wide")

def main():
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
    tab_data, tab_settings, tab_run, tab_results = st.tabs([
        "1. Data", "2. Configure Settings", "3. Run Analysis", "4. Results & Report"
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
            with st.expander("View Data"):
                st.dataframe(st.session_state.data)

    # --- 2. Settings Tab ---
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
