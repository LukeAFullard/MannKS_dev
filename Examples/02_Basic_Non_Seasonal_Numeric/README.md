
# Example 2: Basic Non-Seasonal Trend Test (Numeric Time)

This example demonstrates the simplest use case of the `MannKenSen` package: performing a non-seasonal trend test on a dataset with a simple numeric time vector.

## Script: `run_example.py`
The script performs the following actions:
1.  Generates a synthetic dataset with 50 data points, a clear upward trend, and a simple integer time vector (`t = [0, 1, 2, ...]`).
2.  Calls the `mks.trend_test` function to perform the analysis.
3.  Captures the key results and dynamically generates this `README.md` file, embedding the results below.

## Results
The `trend_test` function returns a `namedtuple` containing the full results of the analysis. The most critical fields for interpretation are listed below.


- **Trend Classification:** Highly Likely Increasing
- **Is Trend Significant? (h):** True
- **P-value (p):** 0.0000
- **Sen's Slope:** 0.0938
- **Mann-Kendall Score (s):** 983.0
- **Kendall's Tau:** 0.8024


### Interpretation
-   The **p-value** is very low (well below 0.05), and `h` is `True`, indicating a statistically significant trend.
-   The **Sen's Slope** is positive, confirming the trend is increasing. The value (`~0.1`) is the calculated rate of change, which is consistent with the trend we added to the synthetic data.
-   The **Classification** of "Highly Likely Increasing" provides a clear, human-readable summary of the result.

**Conclusion:** This basic example shows the fundamental workflow for performing a trend test on simple numeric data.
