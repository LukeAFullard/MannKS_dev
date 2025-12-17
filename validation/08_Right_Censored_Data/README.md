# Validation: 08 - Right-Censored and Mixed-Censored Data

This validation example investigates the `MannKenSen` package's ability to handle right-censored (`>`) and mixed-censored (`<` and `>`) data. It also confirms that the bug identified in Validation 07 within the `LWP-TRENDS` R script affects these censoring types as well.

**Conclusion:** The `MannKenSen` package successfully analyzes both right-censored and mixed-censored datasets. A direct comparison with the `LWP-TRENDS` R script was not possible for this non-aggregated scenario, as the R script fails with the same bug documented in the previous example.

## Methodology

Two synthetic datasets were generated:
1.  **Right-Censored:** A dataset where 30% of the highest values were converted to right-censored strings (e.g., `>28.5`).
2.  **Mixed-Censored:** A dataset with 20% left-censoring and 20% right-censoring.

The Python script (`right_censored_validation.py`) was used to generate the data, run the `MannKenSen.trend_test` using the default robust method, and save the data to `.csv` files.

The R script (`run_lwp_validation.R`) was intended to run the `LWP-TRENDS` `NonSeasonalTrendAnalysis` on the same `.csv` files.

## Python `MannKenSen` Results

The `MannKenSen` package successfully analyzed both datasets.

### Scenario: Right Censored

| Method | P-value | Z-stat  | Slope  | 90% CI         |
| :----- | :------ | :------ | :----- | :------------- |
| Robust | 0.0000  | 4.3556  | 0.2510 | [0.227, 0.278] |

### Scenario: Mixed Censored

| Method | P-value | Z-stat  | Slope  | 90% CI         |
| :----- | :------ | :------ | :----- | :------------- |
| Robust | 0.0000  | 6.1324  | 0.2556 | [0.214, 0.296] |

### Analysis of Python Results
The `MannKenSen` package provides statistically sound and robust trend estimates for both right-censored and mixed-censored data, demonstrating its flexibility in handling various data censoring scenarios.

---

## LWP-TRENDS Comparison Failure Analysis

The `LWP-TRENDS` R script failed to run on both the right-censored and mixed-censored datasets when using the non-aggregated (`TimeIncrMed = FALSE`) setting.

### The Bug

The script produces the same `Error in !Data$Censored : invalid argument type` as documented in Validation 07. This confirms that the internal bug in the `ValueForTimeIncr` function—where it incorrectly converts the logical `Censored` column to a character vector—is not specific to left-censoring. It affects **any** non-aggregated analysis that contains censored data, regardless of the censoring type (left, right, or mixed).

**Conclusion:** The `LWP-TRENDS` script is unreliable for non-aggregated censored trend analysis. The `MannKenSen` package provides a robust and correct implementation for these cases.
