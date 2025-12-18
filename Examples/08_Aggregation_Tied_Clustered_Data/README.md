# Example 8: Aggregation for Tied and Clustered Data

This example demonstrates how the temporal aggregation feature in `MannKenSen` can be used to solve two common data issues:
1.  **Tied Timestamps:** When multiple measurements are recorded at the exact same time.
2.  **Clustered Data:** When sampling frequency is inconsistent, leading to dense clusters of data in certain periods.

Both issues can bias the Sen's slope calculation by giving disproportionate weight to periods with more data. Temporal aggregation resolves this by ensuring each time period contributes a single, representative value to the trend analysis.

## Key Concepts

The `trend_test` function includes two key parameters for aggregation:
-   `agg_method`: Specifies the method used to aggregate data within a period (e.g., `'median'`, `'mean'`, `'robust_median'`).
-   `agg_period`: Specifies the time window for aggregation when using datetimes (e.g., `'year'`, `'month'`, `'day'`).

When aggregation is enabled, the function first groups the data by the specified `agg_period`, calculates a single value for each group using the `agg_method`, and then performs the Mann-Kendall test on the aggregated, evenly-weighted data.

## Script: `run_example.py`
The script creates a synthetic dataset with an increasing trend that exhibits both data clustering (four measurements in March 2013) and tied timestamps (two measurements on the same day in June 2014).

The script analyzes the data twice:
1.  **Without Aggregation (`agg_method='none'`):** This shows the raw analysis. The output includes an "analysis note" warning that the Sen's slope may be affected by the tied timestamps.
2.  **With Annual Aggregation (`agg_method='median'`, `agg_period='year'`):** This calculates the median value for each year, creating a temporally balanced dataset. The warning disappears, and the resulting trend is more robust.

## Results

### Aggregated Analysis Plot
-   **`aggregation_plot.png`**:
    ![Aggregation Plot](aggregation_plot.png)

### Output Analysis (`aggregation_output.txt`)

The text output file clearly shows the difference between the two approaches.

-   **Without Aggregation:** The result includes `analysis_notes=['WARNING: Sen slope may be affected by tied timestamps']`.
-   **With Aggregation:** The analysis notes are empty, and the calculated slope and confidence intervals are based on the more reliable, aggregated data. The script also converts the raw slope (in units/second) to a more interpretable annual slope.

**Conclusion:** Temporal aggregation is a powerful tool for improving the accuracy and reliability of trend analysis on real-world data, which is often messy and irregularly sampled.
