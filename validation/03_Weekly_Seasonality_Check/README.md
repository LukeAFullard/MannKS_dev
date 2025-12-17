# Validation 03: Weekly Seasonality Check

This validation demonstrates and compares the weekly seasonality detection and seasonal trend analysis capabilities of the Python `MannKenSen` package and the LWP-TRENDS R script.

## Description

The validation uses a synthetic dataset of daily values generated over five years. A strong weekly pattern is embedded in the data: values are consistently lower on weekends (Saturday and Sunday) compared to weekdays. A small amount of random noise is added, but no long-term trend is introduced.

Both the Python and R scripts perform two main tasks:
1.  **Seasonality Test:** They use a statistical test (Kruskal-Wallis) to determine if a significant weekly pattern exists in the data.
2.  **Seasonal Trend Analysis:** They perform a seasonal Mann-Kendall test and calculate a seasonal Sen's slope, using the day of the week as the "season".

## How to Run

1.  **Generate Data & Run Python Analysis:**
    Execute the Python script to generate the `validation_data.csv` and run the `MannKenSen` analysis.
    ```bash
    python3 validation/03_Weekly_Seasonality_Check/weekly_seasonality_validation.py
    ```

2.  **Run R Analysis:**
    Execute the R script to run the LWP-TRENDS analysis on the same data.
    ```bash
    Rscript validation/03_Weekly_Seasonality_Check/run_lwp_validation.R
    ```

## Results Comparison

After a thorough investigation, the R script was modified to disable its default data aggregation, allowing for a direct, apples-to-apples comparison with the Python package's default behavior.

| Metric                 | Python (`MannKenSen`) | R (`LWP-TRENDS`, No Aggregation) |
| ---------------------- | --------------------- | -------------------------------- |
| **Seasonality Test**   |
| P-value                | 0.0000                | 0.0007                           |
| Seasonal Detected      | True                  | True                             |
| **Trend Analysis**     |
| Classification         | No Trend              | As likely as not                 |
| P-value                | 0.2465                | 0.2465                           |
| Sen's Slope            | 0.0000                | 0.0000                           |
| Slope 90% C.I.         | (-0.0000, 0.0000)     | (-0.0002, 0.0002)                |

### Analysis of Results

*   **Alignment:** With the inappropriate default data aggregation disabled in the R script (by setting `TimeIncrMed=FALSE` and `UseMidObs=FALSE`), the results from both the Python and R libraries are now in excellent agreement.

*   **Conclusion:** Both analyses correctly identify the strong weekly seasonality and, most importantly, both correctly conclude that there is **no statistically significant long-term trend** (p ≈ 0.2465). Both calculate a Sen's slope of 0.0000, which is the expected result for a dataset with no underlying trend.

This validation confirms that the underlying statistical methods of `MannKenSen` and LWP-TRENDS are consistent when applied to the same dataset without aggregation. The initial discrepancy was due to a default setting in the LWP-TRENDS script that is intended for low-frequency data and is not suitable for this high-frequency daily dataset.
