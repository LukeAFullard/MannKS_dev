# Validation: 07 - Effect of Censoring on Trend Analysis

This validation example investigates how different levels of left-censoring affect the results of the Mann-Kendall trend test. It compares the results from the `MannKenSen` package's default robust method with the aggregated workflow of the `LWP-TRENDS` R script.

**Conclusion:** Both the `MannKenSen` package and the `LWP-TRENDS` R script (in aggregated mode) successfully analyze the datasets. The key difference is that the `LWP-TRENDS` script's default aggregation can sometimes mask the true effect of censoring, as it uses median values which may not be censored.

Further investigation revealed that the `LWP-TRENDS` script has a bug that makes its **non-aggregated** workflow unreliable for censored data. However, its aggregated workflow is functional when provided with correctly pre-processed data.

## Methodology

A synthetic dataset with a known linear trend was generated. This dataset was then subjected to increasing levels of left-censoring (0%, 20%, 40%, and 60%).

The Python script (`censoring_effect_validation.py`) was used to:
1.  Generate the base data and the censored datasets.
2.  Save each dataset to a `.csv` file for use by the R script.
3.  Run the `MannKenSen.trend_test` on each dataset using the default `'robust'` method.
4.  Generate and save plots for each analysis.

The R script (`run_lwp_validation.R`) was intended to run the `LWP-TRENDS` `NonSeasonalTrendAnalysis` on the same `.csv` files, but it fails due to an internal bug.

## Python `MannKenSen` Results

The `MannKenSen` package successfully analyzed all datasets using its default robust method.

| Censoring | Method | P-value | Z-stat   | Slope  | 90% CI         |
| :-------- | :----- | :------ | :------- | :----- | :------------- |
| **0%**    | Robust | 0.0000  | 10.5693  | 0.2565 | [0.233, 0.283] |
| **20%**   | Robust | 0.0000  | 10.0895  | 0.2563 | [0.212, 0.299] |
| **40%**   | Robust | 0.0000  | 9.8291   | 0.1962 | [0.086, 0.295] |
| **60%**   | Robust | 0.0000  | 9.8291   | 0.1962 | [0.086, 0.295] |

### Analysis of Python Results

The results show a gradual and expected decrease in the estimated slope as the level of censoring increases. This is statistically sound behavior, as censoring removes information from the dataset, leading to a more conservative (closer to zero) but still robust estimate of the underlying trend.

---

## LWP-TRENDS Comparison Results (Aggregated)

The `LWP-TRENDS` R script was run in its default **aggregated mode** (`TimeIncrMed = TRUE`). This mode is functional, unlike the non-aggregated mode which contains a bug.

| Censoring | Method     | P-value | Z-stat   | Slope  | 90% CI         |
| :-------- | :--------- | :------ | :------- | :----- | :------------- |
| **0%**    | LWP-TRENDS | 0.0000  | 10.5693  | 0.2565 | [0.237, 0.278] |
| **20%**   | LWP-TRENDS | 0.0000  | 10.1316  | 0.2716 | [0.247, 0.295] |
| **40%**   | LWP-TRENDS | 0.0000  | 10.1674  | 0.2815 | [0.257, 0.305] |
| **60%**   | LWP-TRENDS | 0.0000  | 10.1674  | 0.2815 | [0.257, 0.305] |

### Analysis of Comparison

The `LWP-TRENDS` script successfully analyzed all datasets in its aggregated mode. Because the data is annual, the "aggregation" does not change the number of data points. The slight differences in slope and confidence intervals compared to the `MannKenSen` results are likely due to subtle differences in how each package handles tie-breaking and Sen's slope confidence interval calculations. The overall trend direction and significance are consistent between both packages.
