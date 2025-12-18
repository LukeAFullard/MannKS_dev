
# Example 8: Aggregation for Tied and Clustered Data

This example demonstrates how temporal aggregation can solve two common data issues: tied timestamps (multiple measurements at the same time) and clustered data (inconsistent sampling frequency). Both can bias the Sen's slope calculation.

## Key Concepts
The `trend_test` function includes `agg_method` and `agg_period` parameters. When enabled, the function groups data by the specified period (e.g., 'year'), calculates a single value for each group, and then performs the trend test on the aggregated, evenly-weighted data.

## Script: `run_example.py`
The script creates a dataset with both data clustering and tied timestamps. It analyzes the data twice: once without aggregation and once with annual median aggregation.

## Results

### Analysis Without Aggregation
The raw analysis flags the tied timestamps as a potential issue in the `analysis_notes`.
- **Classification:** Highly Likely Increasing\n- **P-value:** 4.25e-06\n- **Analysis Notes:** ['tied timestamps present without aggregation']\n

### Analysis With Annual Aggregation
Aggregating the data to an annual median resolves the issue, providing a more robust trend estimate.
- **Classification:** Highly Likely Increasing\n- **P-value:** 8.44e-06\n- **Annual Slope:** 0.4584\n

### Aggregated Analysis Plot (`aggregation_plot.png`)
The plot shows the trend calculated from the aggregated data.
![Aggregation Plot](aggregation_plot.png)

**Conclusion:** Temporal aggregation is a powerful tool for improving the accuracy of trend analysis on messy, irregularly sampled real-world data.
