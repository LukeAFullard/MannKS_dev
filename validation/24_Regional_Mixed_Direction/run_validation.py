
import os
import sys

# Ensure validation utils can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from regional_validation_utils import generate_site_data, run_python_regional_test, run_r_regional_test, create_markdown_report

import pandas as pd
import numpy as np

def run_v24():
    scenarios = []

    # --- Scenario 1: Aggregate Increasing (Mixed) ---
    print("Running Scenario 1: Aggregate Increasing (Mixed)...")
    sites = []
    # 4 increasing, 1 decreasing
    for i in range(4):
        sites.append(generate_site_data(f"Site_Inc_{i+1}", trend_type='increasing'))
    sites.append(generate_site_data(f"Site_Dec_1", trend_type='decreasing'))
    data_sc1 = pd.concat(sites)

    py_res_sc1, py_trends_sc1 = run_python_regional_test(data_sc1)
    r_res_sc1 = run_r_regional_test(data_sc1, py_trends_sc1)

    scenarios.append({
        'name': 'Aggregate Increasing',
        'py_res': py_res_sc1,
        'r_res': r_res_sc1
    })

    # --- Scenario 2: Aggregate Decreasing (Mixed) ---
    print("Running Scenario 2: Aggregate Decreasing (Mixed)...")
    sites = []
    # 4 decreasing, 1 increasing
    for i in range(4):
        sites.append(generate_site_data(f"Site_Dec_{i+1}", trend_type='decreasing'))
    sites.append(generate_site_data(f"Site_Inc_1", trend_type='increasing'))
    data_sc2 = pd.concat(sites)

    py_res_sc2, py_trends_sc2 = run_python_regional_test(data_sc2)
    r_res_sc2 = run_r_regional_test(data_sc2, py_trends_sc2)

    scenarios.append({
        'name': 'Aggregate Decreasing',
        'py_res': py_res_sc2,
        'r_res': r_res_sc2
    })

    # --- Scenario 3: Aggregate Indeterminate (Balanced) ---
    print("Running Scenario 3: Aggregate Indeterminate (Balanced)...")
    sites = []
    # 2 increasing, 2 decreasing, 1 stable
    sites.append(generate_site_data("Site_Inc_1", trend_type='increasing'))
    sites.append(generate_site_data("Site_Inc_2", trend_type='increasing'))
    sites.append(generate_site_data("Site_Dec_1", trend_type='decreasing'))
    sites.append(generate_site_data("Site_Dec_2", trend_type='decreasing'))
    sites.append(generate_site_data("Site_Stab_1", trend_type='stable'))
    data_sc3 = pd.concat(sites)

    py_res_sc3, py_trends_sc3 = run_python_regional_test(data_sc3)
    r_res_sc3 = run_r_regional_test(data_sc3, py_trends_sc3)

    scenarios.append({
        'name': 'Aggregate Indeterminate',
        'py_res': py_res_sc3,
        'r_res': r_res_sc3
    })

    # Generate Report
    report = create_markdown_report(
        "V-24: Regional Trend with Mixed Directions",
        "Verification of regional trend aggregation for sites with conflicting trend directions.",
        scenarios
    )

    with open("README.md", "w") as f:
        f.write(report)

    print("V-24 Complete. Report generated.")

if __name__ == "__main__":
    run_v24()
