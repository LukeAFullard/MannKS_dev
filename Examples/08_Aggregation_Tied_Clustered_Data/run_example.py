import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/08_Aggregation_Tied_Clustered_Data'
plot_file = os.path.join(output_dir, 'aggregation_plot.png')
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate Data ---
np.random.seed(42)
dates = pd.to_datetime([
    '2010-07-01', '2011-07-01', '2012-07-01',
    '2013-03-01', '2013-03-05', '2013-03-10', '2013-03-15', # Clustered
    '2014-06-15', '2014-06-15', # Tied
    '2015-07-01', '2016-07-01', '2017-07-01', '2018-07-01', '2019-07-01'
])
values = np.array([5, 5.5, 6, 6.2, 6.3, 6.1, 6.4, 7, 6.8, 7.5, 8, 8.2, 8.5, 9])

# --- 2. Run Analyses ---
result_no_agg = mks.trend_test(x=values, t=dates, agg_method='none')
result_agg = mks.trend_test(
    x=values,
    t=dates,
    agg_method='median',
    agg_period='year',
    plot_path=plot_file
)

# --- 3. Format Results and Generate README ---
no_agg_summary = (
    "- **Classification:** {}\\n"
    "- **P-value:** {:.2e}\\n"
    "- **Analysis Notes:** {}\\n"
).format(result_no_agg.classification, result_no_agg.p, result_no_agg.analysis_notes)

annual_slope = result_agg.slope * 365.25 * 24 * 60 * 60
agg_summary = (
    "- **Classification:** {}\\n"
    "- **P-value:** {:.2e}\\n"
    "- **Annual Slope:** {:.4f}\\n"
).format(result_agg.classification, result_agg.p, annual_slope)

readme_content = """
# Example 8: Aggregation for Tied and Clustered Data

This example demonstrates how temporal aggregation can solve two common data issues: tied timestamps (multiple measurements at the same time) and clustered data (inconsistent sampling frequency). Both can bias the Sen's slope calculation.

## Key Concepts
The `trend_test` function includes `agg_method` and `agg_period` parameters. When enabled, the function groups data by the specified period (e.g., 'year'), calculates a single value for each group, and then performs the trend test on the aggregated, evenly-weighted data.

## Script: `run_example.py`
The script creates a dataset with both data clustering and tied timestamps. It analyzes the data twice: once without aggregation and once with annual median aggregation.

## Results

### Analysis Without Aggregation
The raw analysis flags the tied timestamps as a potential issue in the `analysis_notes`.
{}

### Analysis With Annual Aggregation
Aggregating the data to an annual median resolves the issue, providing a more robust trend estimate.
{}

### Aggregated Analysis Plot (`aggregation_plot.png`)
The plot shows the trend calculated from the aggregated data.
![Aggregation Plot](aggregation_plot.png)

**Conclusion:** Temporal aggregation is a powerful tool for improving the accuracy of trend analysis on messy, irregularly sampled real-world data.
""".format(no_agg_summary, agg_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'aggregation_output.txt')):
    os.remove(os.path.join(output_dir, 'aggregation_output.txt'))

print("Successfully generated README and plot for Example 8.")
