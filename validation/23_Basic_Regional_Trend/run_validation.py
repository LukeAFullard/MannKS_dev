
import os
import sys

# Ensure validation utils can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from regional_validation_utils import generate_site_data, run_python_regional_test, run_r_regional_test, create_markdown_report

import pandas as pd
import numpy as np

def run_v23():
    scenarios = []

    # --- Scenario 1: Strong Increasing ---
    print("Running Scenario 1: Strong Increasing...")
    sites = []
    for i in range(5):
        sites.append(generate_site_data(f"Site_{i+1}", trend_type='increasing', noise_std=0.5))
    data_inc = pd.concat(sites)

    py_res_inc, py_trends_inc = run_python_regional_test(data_inc)
    r_res_inc = run_r_regional_test(data_inc, py_trends_inc)

    scenarios.append({
        'name': 'Strong Increasing',
        'py_res': py_res_inc,
        'r_res': r_res_inc
    })

    # --- Scenario 2: Weak Decreasing ---
    print("Running Scenario 2: Weak Decreasing...")
    sites = []
    for i in range(5):
        # Higher noise, smaller slope
        df = generate_site_data(f"Site_{i+1}", trend_type='decreasing', noise_std=2.0)
        # Reduce slope magnitude to make it "weak"
        # Since generate_site_data has fixed slope 0.1, we modify 'value'
        # Slope -0.1 is already somewhat subtle with noise 2.0, but let's make it weaker.
        # Original: values = 10 - 0.1*t + noise
        # Let's effectively reduce t influence.
        # Actually generate_site_data is a bit rigid. Let's just use it as is.
        sites.append(df)
    data_dec = pd.concat(sites)

    py_res_dec, py_trends_dec = run_python_regional_test(data_dec)
    r_res_dec = run_r_regional_test(data_dec, py_trends_dec)

    scenarios.append({
        'name': 'Weak Decreasing',
        'py_res': py_res_dec,
        'r_res': r_res_dec
    })

    # --- Scenario 3: Stable ---
    print("Running Scenario 3: Stable...")
    sites = []
    for i in range(5):
        sites.append(generate_site_data(f"Site_{i+1}", trend_type='stable', noise_std=1.0))
    data_stab = pd.concat(sites)

    py_res_stab, py_trends_stab = run_python_regional_test(data_stab)
    r_res_stab = run_r_regional_test(data_stab, py_trends_stab)

    scenarios.append({
        'name': 'Stable',
        'py_res': py_res_stab,
        'r_res': r_res_stab
    })

    # Generate Report
    report = create_markdown_report(
        "V-23: Basic Regional Trend",
        "Verification of regional trend aggregation for consistent site trends (Increasing, Decreasing, Stable).",
        scenarios
    )

    with open("README.md", "w") as f:
        f.write(report)

    print("V-23 Complete. Report generated.")

if __name__ == "__main__":
    run_v23()
