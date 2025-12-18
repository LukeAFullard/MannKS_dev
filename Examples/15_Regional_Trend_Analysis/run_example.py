import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/15_Regional_Trend_Analysis'
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate Data ---
np.random.seed(42)
sites = ['Site A', 'Site B', 'Site C']
years = np.arange(2010, 2021)
n_years = len(years)
# Site A: Clear increasing trend
trend_a = np.linspace(0, 5, n_years); noise_a = np.random.normal(0, 1, n_years)
values_a = 10 + trend_a + noise_a
# Site B: Weaker increasing trend
trend_b = np.linspace(0, 2, n_years); noise_b = np.random.normal(0, 1, n_years)
values_b = 15 + trend_b + noise_b
# Site C: No clear trend (stable)
trend_c = np.linspace(0, 0, n_years); noise_c = np.random.normal(0, 1, n_years)
values_c = 12 + trend_c + noise_c
# Combine into a single DataFrame
df_a = pd.DataFrame({'site': 'Site A', 'year': years, 'value': values_a})
df_b = pd.DataFrame({'site': 'Site B', 'year': years, 'value': values_b})
df_c = pd.DataFrame({'site': 'Site C', 'year': years, 'value': values_c})
regional_data = pd.concat([df_a, df_b, df_c], ignore_index=True)

# --- 2. Run Analyses ---
site_results = []
for site in sites:
    site_data = regional_data[regional_data['site'] == site]
    result = mks.trend_test(x=site_data['value'], t=site_data['year'])
    site_results.append(result)

results_df = pd.DataFrame(site_results)
results_df['site'] = sites
regional_result = mks.regional_test(
    trend_results=results_df,
    time_series_data=regional_data,
    site_col='site',
    value_col='value',
    time_col='year',
    s_col='s',
    c_col='C'
)

# --- 3. Format Results and Generate README ---
site_a_summary = "- Site A Trend: {}\\n".format(site_results[0].classification)
site_b_summary = "- Site B Trend: {}\\n".format(site_results[1].classification)
site_c_summary = "- Site C Trend: {}\\n".format(site_results[2].classification)
regional_summary = (
    "- **Regional Trend Direction:** {}\\n"
    "- **Aggregate Trend Confidence (CT):** {:.4f}\\n"
    "- **Number of Sites (M):** {}\\n"
).format(regional_result.DT, regional_result.CT, regional_result.M)

readme_content = """
# Example 15: Regional Trend Analysis

This example demonstrates how to use the `regional_test` function to aggregate trend results from multiple sites to determine if there is a significant trend across an entire region.

## Key Concepts
A regional test answers the question: "Is there a general, region-wide trend?" It works by:
1.  Performing a trend test on each individual site.
2.  Aggregating the S-statistics and their variances.
3.  Adjusting for inter-site correlation.
4.  Performing a final Z-test on the aggregated results.

## Script: `run_example.py`
The script simulates a scenario with three sites: two with increasing trends of different strengths and one with no trend. It analyzes each site individually and then passes the results to the `regional_test` function.

## Results
Despite one site showing no trend, the regional test combines the evidence to find an overall trend.

### Individual Site Results
{}
{}
{}

### Regional Test Result
{}

**Conclusion:** The `regional_test` function provides a statistically sound method for assessing large-scale environmental changes by synthesizing trend information from multiple time series.
""".format(site_a_summary, site_b_summary, site_c_summary, regional_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'regional_analysis_output.txt')):
    os.remove(os.path.join(output_dir, 'regional_analysis_output.txt'))

print("Successfully generated README for Example 15.")
