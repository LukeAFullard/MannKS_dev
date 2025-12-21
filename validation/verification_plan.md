# MannKenSen Verification Plan

This document outlines a comprehensive plan for verifying the `mannkensen` Python package against the original LWP-TRENDS R script. The goal is to ensure that `mannkensen`'s LWP-emulation mode produces results that are as close as possible to the R script, and to clearly document any intentional deviations.

## Verification Methodology

For each verification case, three analyses will be performed and their results compared:

1.  **`mannkensen` (Standard):** A standard run of the relevant `mannkensen` function (`trend_test` or `seasonal_trend_test`) using its default, robust statistical methods.
2.  **`mannkensen` (LWP Mode):** A run of the `mannkensen` function with all LWP-compatibility parameters enabled. This typically includes:
    *   `mk_test_method='lwp'`
    *   `ci_method='lwp'`
    *   `agg_method='lwp'` (or other LWP-style aggregation)
    *   `sens_slope_method='lwp'`
    *   `tie_break_method='lwp'` (for non-seasonal tests)
3.  **LWP-TRENDS R Script:** A run of the original `LWPTrends_v2502.r` script using `rpy2` to execute the analysis on the identical synthetic dataset.

All data used for these tests will be synthetically generated to provide full control over the inputs and expected outcomes.

---

## Verification Scenarios

### Category 1: Basic Non-Seasonal Trends

**V-01: Simple Increasing Trend**
*   **Objective:** Verify that all methods correctly identify a statistically significant, positive trend in a simple, non-seasonal, uncensored dataset.
*   **Data Description:** Linear data with a positive slope and random noise.
*   **Expected Outcome:** All three methods should report a significant increasing trend. The Sen's slope, p-value, and confidence intervals from `mannkensen-lwp` and the R script are expected to be very similar.

**V-02: Simple Decreasing Trend**
*   **Objective:** Verify that all methods correctly identify a statistically significant, negative trend.
*   **Data Description:** Linear data with a negative slope and random noise.
*   **Expected Outcome:** All methods should report a significant decreasing trend. `mannkensen-lwp` and R results should align closely.

**V-03: No Trend**
*   **Objective:** Verify that all methods correctly identify a lack of trend.
*   **Data Description:** Random data with no underlying slope.
*   **Expected Outcome:** All three methods should report "no trend" with a high p-value.

**V-04: Data with Tied Values**
*   **Objective:** Test the handling of tied values in the data vector.
*   **Data Description:** Data with a clear trend but multiple repeated values.
*   **Expected Outcome:** The `tau_method='b'` (default) in `mannkensen` should handle this robustly. The `mannkensen-lwp` run, with its specific `tie_break_method`, should produce results very close to the R script's tie handling.

### Category 2: Censored Data

**V-05: Left-Censored Increasing Trend**
*   **Objective:** Verify the handling of left-censored (`<`) data.
*   **Data Description:** Data with a positive slope where some of the lower values are left-censored.
*   **Expected Outcome:** `mannkensen-lwp` (using `sens_slope_method='lwp'`) should produce a slope and p-value very similar to the R script. The standard `mannkensen` run may differ slightly due to its more robust handling of ambiguous slopes.

**V-06: Right-Censored Increasing Trend**
*   **Objective:** Verify the handling of right-censored (`>`) data.
*   **Data Description:** Data with a positive slope where some of the higher values are right-censored.
*   **Expected Outcome:** This is a key test. `mannkensen-lwp` (with `mk_test_method='lwp'`) should closely match the R script's heuristic of replacing `>` values. The standard `mannkensen` run (`mk_test_method='robust'`) is expected to produce a more conservative (potentially non-significant) result.

**V-07: Mixed Censoring**
*   **Objective:** Test a combination of left- and right-censored data.
*   **Data Description:** A dataset containing both `<` and `>` values.
*   **Expected Outcome:** Similarities and differences between the methods are expected to follow the patterns seen in V-05 and V-06.

**V-08: High Censor Rule (`hicensor`)**
*   **Objective:** Verify the implementation of the "high censor" rule.
*   **Data Description:** Data with multiple censoring levels, where some uncensored values fall below the highest censoring limit.
*   **Expected Outcome:** Both `mannkensen` and the R script (with `HiCensor=TRUE`) should treat the low uncensored values as censored, leading to a different result than a standard run. The outputs of the LWP-mode and R script should be nearly identical.

### Category 3: Seasonal Data

**V-09: Monthly Seasonal Increasing Trend**
*   **Objective:** Verify the seasonal test on a simple monthly dataset.
*   **Data Description:** Monthly data with an overall increasing trend but with a clear seasonal cycle.
*   **Expected Outcome:** All methods should detect the significant increasing trend. `mannkensen-lwp` and the R script should have very similar outputs.

**V-10: Quarterly Seasonal Data**
*   **Objective:** Test seasonality with a different period (quarterly).
*   **Data Description:** Quarterly data with an underlying trend.
*   **Expected Outcome:** All methods should correctly handle the quarterly seasonality.

**V-11: Seasonal Data with Missing Seasons**
*   **Objective:** Verify behavior when entire seasons are missing from the data.
*   **Data Description:** A seasonal dataset with one or more seasons (e.g., all "July" data) completely removed.
*   **Expected Outcome:** The tests should run without error and produce a result based on the remaining seasons.

**V-12: Seasonal Data with Censoring**
*   **Objective:** Test the combination of seasonality and censored data.
*   **Data Description:** Monthly data with an increasing trend and some left-censored values.
*   **Expected Outcome:** The results should reflect the combined complexities, with `mannkensen-lwp` and R aligning closely.

### Category 4: Aggregation and Data Quality

**V-13: LWP Aggregation (`agg_method='lwp'`)**
*   **Objective:** Verify the LWP-style temporal aggregation.
*   **Data Description:** A dataset with multiple observations per time period (e.g., several samples per year for a non-seasonal test).
*   **Expected Outcome:** `mannkensen-lwp` with `agg_method='lwp'` should produce a result based on one value per period, closely matching the R script's aggregated workflow (`TimeIncrMed=TRUE`). The standard `mannkensen` run with `agg_method='none'` will produce a different result and a warning about tied timestamps.

**V-14: Insufficient Data**
*   **Objective:** Verify how systems handle datasets that are too small for a valid trend test.
*   **Data Description:** A dataset with very few data points (e.g., n < 5).
*   **Expected Outcome:** All methods should return a result indicating "insufficient data" or produce NA values for the statistical outputs. The `AnalysisNote` from the R script should be consistent with the `analysis_notes` from `mannkensen`.

**V-15: All Values Censored**
*   **Objective:** Verify behavior when all data points are censored.
*   **Data Description:** A dataset where every value is a left-censored value (e.g., `<5`, `<5`, `<5`).
*   **Expected Outcome:** All systems should gracefully handle this and report that no trend can be calculated.

**V-16: Long Run of Identical Values**
*   **Objective:** Verify the data quality check for long runs of a single value.
*   **Data Description:** A dataset where a large proportion of the values are identical and consecutive.
*   **Expected Outcome:** Both `mannkensen` and the R script should produce an "Analysis Note" warning about the long run of identical values.

### Category 5: Parameter-Specific Tests

**V-17: Confidence Interval Method (`ci_method`)**
*   **Objective:** Isolate and verify the two different confidence interval calculation methods.
*   **Data Description:** A standard dataset with a clear trend.
*   **Expected Outcome:** The confidence intervals from `mannkensen-lwp` (`ci_method='lwp'`) should match the R script's interpolated results. The standard `mannkensen` run (`ci_method='direct'`) will produce slightly different intervals due to its direct indexing approach.

**V-18: `lt_mult` and `gt_mult` Parameters**
*   **Objective:** Test the effect of the Sen's slope multipliers for censored data.
*   **Data Description:** A carefully crafted censored dataset where the median slope is sensitive to the value of a single ambiguous pair.
*   **Expected Outcome:** This is a difficult test to construct. The goal is to show that changing `lt_mult` and `gt_mult` in `mannkensen` affects the final slope, and that the default values produce a slope consistent with the R script's internal logic.

**V-19: Unequally Spaced Time Series**
*   **Objective:** Verify a core feature of `mannkensen` on a non-seasonal, unequally spaced time series.
*   **Data Description:** Data with a clear trend but with random, non-uniform time gaps between samples.
*   **Expected Outcome:** Both `mannkensen` and `mannkensen-lwp` should correctly calculate the Sen's slope using the true time differences. The R script, which uses integer time ranks, is expected to produce a different variance, p-value, and confidence intervals, but a similar slope. This test highlights a key methodological difference.

**V-20: Numeric Time Vector**
*   **Objective:** Verify that the functions work correctly with a simple numeric time vector instead of datetimes.
*   **Data Description:** Data with an increasing trend, where the time vector is a simple array of numbers (e.g., years as `[2000, 2001.5, 2002.7]`).
*   **Expected Outcome:** All `mannkensen` functions should execute correctly. The R script may require specific column naming (`Year`) and data types, highlighting its comparative inflexibility. The Sen's slope unit should correctly be reported as "per unit of t".
