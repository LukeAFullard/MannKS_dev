# Validation 04: Aggregation Example

This validation demonstrates and compares how the Python `MannKenSen` package and the LWP-TRENDS R script handle datasets with multiple observations within a single time period.

## Description

The validation uses a synthetic dataset of monthly values generated over 15 years, with a clear increasing trend. Several duplicate observations are deliberately introduced into the same time periods to test the aggregation logic.

The validation compares three different analysis methods:
1.  **Python (`agg_method='none'`):** The `seasonal_trend_test` is run without aggregation. This method is not statistically robust for data with tied timestamps but is included to show the raw trend.
2.  **Python (`agg_method='median'`):** The `seasonal_trend_test` is run with median aggregation, which is the correct approach for this dataset in the `MannKenSen` library.
3.  **R (LWP-TRENDS):** The R script is run using its default behavior, which also aggregates multiple observations within a time period using a median.

## How to Run

1.  **Generate Data & Run Python Analysis:**
    Execute the Python script to generate the `validation_data.csv` and run both `MannKenSen` analyses.
    ```bash
    python3 validation/04_Aggregation_Example/aggregation_validation.py
    ```

2.  **Run R Analysis:**
    Execute the R script to run the LWP-TRENDS analysis on the same data.
    ```bash
    Rscript validation/04_Aggregation_Example/run_lwp_validation.R
    ```

## Results Comparison

After correcting the data generation to use a consistent `datetime`-based source for all scripts, the results are now directly comparable.

| Metric           | Python (`agg_method='none'`) | Python (`agg_method='median'`) | R (LWP-TRENDS)         |
| ---------------- | ---------------------------- | ------------------------------ | ---------------------- |
| Classification   | Highly Likely Increasing     | Highly Likely Increasing       | Highly likely          |
| P-value          | 0.0000                       | 0.0000                         | 0.0000                 |
| Sen's Slope      | 1.4932                       | 1.6455                         | 1.6455                 |
| Slope 90% C.I.   | (1.3060, 1.6888)             | (1.5100, 1.7668)               | (1.4838, 1.7660)       |

### Analysis of Results

*   **Conclusion:** With a consistent `datetime`-based dataset, all methods now correctly identify the "Highly Likely Increasing" trend with a p-value of 0.0000.

*   **Aggregation Alignment:** The most important finding is that the Python `agg_method='median'` and the R LWP-TRENDS script now produce identical Sen's slopes (1.6455). This confirms that their median aggregation logic is consistent and that the `MannKenSen` package is a valid Python alternative to the LWP-TRENDS R script for this use case.

*   **Impact of Aggregation:** The non-aggregated Python result has a slightly different slope (1.4932), which is expected as it includes the raw, non-aggregated duplicate data points in its calculation. This result demonstrates the effect and importance of applying a consistent aggregation strategy when dealing with duplicate timestamps.

This validation successfully confirms that the `agg_method='median'` in `MannKenSen` is a correct and robust implementation that matches the behavior of the reference LWP-TRENDS R script.
