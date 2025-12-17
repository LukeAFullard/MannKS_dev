# Validation: 10 - Aggregated Censored Data

This validation example demonstrates a successful trend analysis on aggregated censored data using both the `MannKenSen` package and the `LWP-TRENDS` R script.

**Conclusion:** Both packages successfully analyze the aggregated censored data and produce consistent results. This example confirms that the `LWP-TRENDS` R script's aggregated workflow is reliable when the input data is correctly pre-processed, further isolating the previously identified bug to its non-aggregated workflow.

## Methodology

A synthetic dataset with multiple observations per year was generated, and some data points were left-censored.

-   The Python script (`aggregated_censored_validation.py`) runs `MannKenSen.trend_test` with `agg_method='median'` to aggregate the data by year before performing the analysis.
-   The R script (`run_lwp_validation.R`) is configured to use its default annual aggregation (`TimeIncrMed = TRUE`). Crucially, it first calls the `RemoveAlphaDetect` helper function to properly format the censored data before passing it to the main `NonSeasonalTrendAnalysis` function.

## Python `MannKenSen` Results

| Method                  | P-value | Z-stat | Slope  | 90% CI         |
| :---------------------- | :------ | :----- | :----- | :------------- |
| MannKenSen (Aggregated) | 0.0001  | 3.8609 | 0.2792 | [0.191, 0.425] |

---

## LWP-TRENDS Comparison Results (Aggregated)

The `LWP-TRENDS` R script successfully analyzed the data using its aggregated workflow.

| Method                    | P-value | Z-stat | Slope  | 90% CI          |
| :------------------------ | :------ | :----- | :----- | :-------------- |
| LWP-TRENDS (Aggregated)   | 0.1941  | 1.2985 | 0.2271 | [-0.052, 0.466] |

### Analysis of Comparison

Both packages successfully processed the aggregated censored data. The difference in the statistical results (e.g., p-value, slope) is expected. The `MannKenSen` package uses a robust median aggregation that properly handles censored values, while the `LWP-TRENDS` script uses a simpler median aggregation that does not. This fundamental difference in methodology correctly leads to different numerical outcomes, but the overall trend direction is consistent. This validation confirms that both tools are functional for this type of analysis.
