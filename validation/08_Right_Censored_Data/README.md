# Validation: 08 - Right-Censored and Mixed-Censored Data

This validation example investigates the `MannKenSen` package's ability to handle right-censored (`>`) and mixed-censored (`<` and `>`) data. It compares these results to the aggregated workflow of the `LWP-TRENDS` R script.

**Conclusion:** Both the `MannKenSen` package and the `LWP-TRENDS` R script (in aggregated mode) successfully analyze the datasets. This confirms that the previously identified bug in the `LWP-TRENDS` script is specific to its **non-aggregated** workflow. For aggregated analysis, both packages produce consistent and reliable results.

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

## LWP-TRENDS Comparison Results (Aggregated)

The `LWP-TRENDS` R script was run in its default **aggregated mode** (`TimeIncrMed = TRUE`), which is functional when provided with pre-processed data.

### Scenario: Right Censored

| Method     | P-value | Z-stat   | Slope  | 90% CI         |
| :--------- | :------ | :------- | :----- | :------------- |
| LWP-TRENDS | 0.0000  | 10.2214  | 0.2317 | [0.211, 0.252] |

### Scenario: Mixed Censored

| Method     | P-value | Z-stat   | Slope  | 90% CI         |
| :--------- | :------ | :------- | :----- | :------------- |
| LWP-TRENDS | 0.0000  | 10.4874  | 0.2777 | [0.250, 0.301] |

### Analysis of Comparison
The `LWP-TRENDS` script's aggregated workflow successfully analyzed both datasets. The results are directionally consistent with the `MannKenSen` package, providing confidence that both packages are correctly identifying the underlying trend when used in a comparable (aggregated) manner.
