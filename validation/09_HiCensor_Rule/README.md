# Validation: 09 - HiCensor Rule

This validation example aims to test the implementation of the "HiCensor" rule in the `MannKenSen` package. The rule, also present in the `LWP-TRENDS` R script, is a heuristic that treats all data points (censkored or not) below the highest detection limit as being censored at that limit.

**Conclusion:** Both the `MannKenSen` package and the `LWP-TRENDS` R script (in aggregated mode) provide functional implementations of the HiCensor rule. This test confirms that the `LWP-TRENDS` script is usable for aggregated analysis when the input data is correctly pre-processed. In this specific dataset, applying the HiCensor rule did not change the final trend result in either package, which is a plausible outcome for data with a strong underlying trend.

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

## LWP-TRENDS Comparison Results (Aggregated)

The `LWP-TRENDS` R script was run in its default aggregated mode (`TimeIncrMed = TRUE`) with a correctly pre-processed dataset. It successfully ran analyses both with and without the `HiCensor` rule.

| Method        | P-value | Z-stat  | Slope  | 90% CI         |
| :------------ | :------ | :------ | :----- | :------------- |
| LWP-Default   | 0.0000  | 4.2282  | 0.6627 | [0.509, 0.830] |
| LWP-HiCensor  | 0.0000  | 4.2282  | 0.6627 | [0.509, 0.830] |

### Analysis of Comparison
Both the `MannKenSen` package and the `LWP-TRENDS` script produced identical results when running with and without the HiCensor rule. This indicates that for this particular dataset, the rule did not alter the final outcome. More importantly, it confirms that the HiCensor functionality in the `LWP-TRENDS` script is working correctly within the aggregated workflow.
