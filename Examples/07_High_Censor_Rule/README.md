# Example 7: The High Censor Rule (`hicensor`)

This example demonstrates the `hicensor` rule, a critical feature for handling time series data where laboratory detection limits have improved (decreased) over time. Such changes can create a misleading "paper trend" that does not reflect any real change in the environment.

## Key Concepts

Imagine monitoring a chemical where the lab's detection limit improves from `<10` to `<1` over a decade. Even if the actual concentration of the chemical remains stable and below `1`, the recorded data will show a sequence of `<10`, `<5>`, `<2>`, `<1`, etc. A standard trend test will incorrectly interpret this as a strong decreasing trend.

The `hicensor` rule corrects for this artifact. When `hicensor=True`:
1.  The function scans the entire dataset to find the **highest detection limit** for left-censored data (e.g., the `10` in `<10`).
2.  It then treats **all data points** (both censored and uncensored) that are below this highest limit as if they were censored at that limit.

In our example, all values (`<10`, `<5>`, `<2>`, `<1`) would be treated as `<10`. This effectively transforms the dataset into a series of tied values, correctly removing the artificial trend.

## Script: `run_example.py`
The script generates a synthetic dataset that perfectly illustrates this problem: a time series of left-censored values where the detection limit improves over time, creating a strong artificial decreasing trend.

The script then analyzes the data twice:
1.  **Without `hicensor`:** This shows the incorrect "Highly Likely Decreasing" result.
2.  **With `hicensor=True`:** This shows the corrected "No Trend" result.

## Results

### Original Analysis (Incorrect Trend)
-   **`original_data_plot.png`**:
    ![Original Data Plot](original_data_plot.png)

### Analysis with `hicensor` Rule (Corrected Trend)
-   **`hicensor_rule_plot.png`**:
    ![Hicensor Rule Plot](hicensor_rule_plot.png)

### Output Analysis (`hicensor_output.txt`)

The text output file provides a clear numerical comparison. The initial analysis produces a highly significant p-value, indicating a strong trend. After applying `hicensor=True`, the p-value becomes `1.0`, and the S-statistic becomes `0`, correctly identifying that there is no evidence of a trend in the data once the artifact from changing detection limits is removed.

**Conclusion:** The `hicensor` rule is an essential tool for ensuring the scientific validity of trend analysis on long-term environmental datasets where analytical methods have changed over time.
