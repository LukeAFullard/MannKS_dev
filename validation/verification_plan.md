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

All data used for these tests will be synthetically generated to provide full control over the inputs and expected outcomes. The majority of tests will use monthly data frequency, with a smaller subset using annual data to ensure both are handled correctly.

### Scenario Structure

For each numbered verification case below (e.g., V-01), **three distinct scenarios** will be tested to ensure robustness across different trend characteristics:
*   **Strong Increasing Trend:** A clear, statistically significant positive trend.
*   **Weak Decreasing Trend:** A subtle, statistically significant (or borderline) negative trend.
*   **Stable (No Trend):** Data with no underlying trend, expected to be non-significant.

The results for all three scenarios will be presented in a single summary table for each verification case. No new plots are required for this expanded scope; the focus is on the tabular comparison of statistical results.

## Master Results Tracking

A master CSV file, `validation/master_results.csv`, will be created and updated as part of the verification process. This file will consolidate the key outputs from every single test run. For each test (e.g., "V-01_strong_increasing"), the CSV will contain a row with the following columns:
*   `test_id`: A unique identifier (e.g., "V-01_strong_increasing").
*   `mk_py_slope`, `mk_py_p_value`, `mk_py_lower_ci`, `mk_py_upper_ci`: Results from `mannkensen` (Standard).
*   `lwp_py_slope`, `lwp_py_p_value`, `lwp_py_lower_ci`, `lwp_py_upper_ci`: Results from `mannkensen` (LWP Mode).
*   `r_slope`, `r_p_value`, `r_lower_ci`, `r_upper_ci`: Results from the LWP-TRENDS R Script.
*   `slope_error`: The absolute error (`lwp_py_slope` - `r_slope`).
*   `slope_pct_error`: The percentage error, calculated as `(slope_error / r_slope) * 100`.

This master file will provide a quantitative, high-level overview of the LWP-mode's accuracy and consistency.

---

## Verification Scenarios

### Category 1: Basic Non-Seasonal Trends

**V-01: Simple Trend**
*   **Objective:** Verify that all methods correctly identify trends in a simple, non-seasonal, uncensored dataset.
*   **Data Description:** Annual linear data with random noise. This test uses annual data to ensure compatibility with the `NonSeasonalTrendAnalysis` function in the R script, which is brittle with other data frequencies.

**V-02: Data with Tied Values**
*   **Objective:** Test the handling of tied values in the data vector.
*   **Data Description:** Monthly data with a clear trend but multiple repeated values.

**V-03: Unequally Spaced Time Series**
*   **Objective:** Verify a core feature of `mannkensen` on a non-seasonal, unequally spaced time series.
*   **Data Description:** Data with a clear trend but with random, non-uniform time gaps between samples. This test highlights a key methodological difference where the R script is expected to differ.

**V-04: Numeric Time Vector**
*   **Objective:** Verify that the functions work correctly with a simple numeric time vector instead of datetimes.
*   **Data Description:** Annual data with a trend, where the time vector is a simple array of numbers (e.g., years as `[2000, 2001.5, 2002.7]`).

### Category 2: Censored Data

**V-05: Left-Censored Trend**
*   **Objective:** Verify the handling of left-censored (`<`) data.
*   **Data Description:** Monthly data with a trend where some of the lower values are left-censored.

**V-06: Right-Censored Trend**
*   **Objective:** Verify the handling of right-censored (`>`) data.
*   **Data Description:** Monthly data with a trend where some of the higher values are right-censored.

**V-07: Mixed Censoring**
*   **Objective:** Test a combination of left- and right-censored data.
*   **Data Description:** A monthly dataset containing both `<` and `>` values.

**V-08: High Censor Rule (`hicensor`)**
*   **Objective:** Verify the implementation of the "high censor" rule.
*   **Data Description:** Monthly data with multiple censoring levels, where some uncensored values fall below the highest censoring limit.

### Category 3: Seasonal Data

**V-09: Monthly Seasonal Trend**
*   **Objective:** Verify the seasonal test on a simple monthly dataset.
*   **Data Description:** Monthly data with an overall trend and a clear seasonal cycle.

**V-10: Quarterly Seasonal Data**
*   **Objective:** Test seasonality with a different period (quarterly).
*   **Data Description:** Quarterly data with an underlying trend.

**V-11: Monthly Seasonal with Left-Censoring**
*   **Objective:** Test the combination of monthly seasonality and left-censored data.
*   **Data Description:** Monthly data with a trend, a seasonal cycle, and some left-censored values.

**V-12: Monthly Seasonal with Right-Censoring**
*   **Objective:** Test the combination of monthly seasonality and right-censored data.
*   **Data Description:** Monthly data with a trend, a seasonal cycle, and some right-censored values.

**V-13: Seasonal Data with Missing Seasons**
*   **Objective:** Verify behavior when entire seasons are missing from the data.
*   **Data Description:** A seasonal dataset with one or more seasons (e.g., all "July" data) completely removed.

### Category 4: Regional Trend Test

**V-14: Basic Regional Trend**
*   **Objective:** Verify the `regional_test` function with a simple case.
*   **Data Description:** Data for 3-5 sites, all exhibiting a similar underlying trend. The test will be run for increasing, decreasing, and no-trend scenarios.
*   **Expected Outcome:** The regional test should correctly aggregate the individual site trends and report a significant regional trend (or lack thereof).

**V-15: Regional Trend with Mixed-Direction Sites**
*   **Objective:** Verify the regional test's behavior when sites have conflicting trends.
*   **Data Description:** Data for multiple sites, where some are increasing, some are decreasing, and some are stable.
*   **Expected Outcome:** The regional test should report "No Clear Direction" or a result that correctly reflects the dominant trend direction if one exists.

### Category 5: Data Quality and Edge Cases

**V-16: LWP Aggregation (`agg_method='lwp'`)**
*   **Objective:** Verify the LWP-style temporal aggregation.
*   **Data Description:** A dataset with multiple observations per time period (e.g., several samples per month).

**V-17: Insufficient Data**
*   **Objective:** Verify how systems handle datasets that are too small for a valid trend test.
*   **Data Description:** A dataset with very few data points (e.g., n < 5).

**V-18: All Values Censored**
*   **Objective:** Verify behavior when all data points are censored.
*   **Data Description:** A dataset where every value is a left-censored value (e.g., `<5`, `<5`, `<5`).

**V-19: Long Run of Identical Values**
*   **Objective:** Verify the data quality check for long runs of a single value.
*   **Data Description:** A dataset where a large proportion of the values are identical and consecutive.
