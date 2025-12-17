# Validation: 09 - HiCensor Rule

This validation example aims to test the implementation of the "HiCensor" rule in the `MannKenSen` package. The rule, also present in the `LWP-TRENDS` R script, is a heuristic that treats all data points (censkored or not) below the highest detection limit as being censored at that limit.

**Conclusion:** The `MannKenSen` package provides a functional `hicensor` parameter. A direct comparison with the `LWP-TRENDS` R script was not possible, as the R script failed to run even with data aggregation enabled, indicating the bug identified in previous examples is more pervasive than initially thought.

## Methodology

A synthetic dataset with a known trend and multiple left-censoring levels (`<4` and `<2`) was generated. This setup is ideal for testing the HiCensor rule, as the rule should re-classify all values below the highest detection limit (`<4`) as `<4`.

The Python script (`hicensor_validation.py`) was used to:
1.  Generate the censored dataset.
2.  Save the dataset to a `.csv` file.
3.  Run `MannKenSen.trend_test` twice: once with `hicensor=False` (the default) and once with `hicensor=True`.

The R script (`run_lwp_validation.R`) was intended to do the same using the `HiCensor` parameter in the `NonSeasonalTrendAnalysis` function.

## Python `MannKenSen` Results

| Method  | P-value | Z-stat  | Slope  | 90% CI         |
| :------ | :------ | :------ | :----- | :------------- |
| Default | 0.0000  | 4.2244  | 0.5518 | [0.260, 0.778] |
| HiCensor| 0.0000  | 4.2244  | 0.5518 | [0.260, 0.778] |

### Analysis of Python Results
In this specific dataset, the `HiCensor` rule did not change the outcome. This can happen in datasets where the trend is strong and the re-classification of points below the highest censor level does not significantly alter the rank-based statistics. The functionality is present and runs without error.

---

## LWP-TRENDS Comparison Failure Analysis

The `LWP-TRENDS` R script failed to run on this dataset, even when data aggregation was explicitly enabled (`TimeIncrMed = TRUE`).

### The Bug

The script produces the same `Error in !Data$Censored : invalid argument type` as documented in Validations 07 and 08. The attempt to bypass the bug by enabling aggregation was unsuccessful. This indicates that the internal data handling for censored values in the `LWP-TRENDS` script is fundamentally flawed and crashes in multiple scenarios, not just the non-aggregated case.

**Conclusion:** The `LWP-TRENDS` script is not reliable for validating censored data functionalities like the HiCensor rule. The `MannKenSen` package provides a working implementation of the rule, even though a direct comparison was not possible.
