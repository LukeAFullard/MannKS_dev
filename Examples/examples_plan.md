# Plan for `MannKenSen` Package Examples

This document outlines a plan for creating a comprehensive suite of examples to guide users through the functionality of the `MannKenSen` package. The examples are designed to build upon each other, starting with the simplest use case and progressively introducing more complex features and parameters.

Each example will be self-contained in its own directory within `Examples/` and will include a Python script and a markdown (`.md`) file explaining the process, code, and results with embedded plots.

---

### Example 1: Basic Non-Seasonal Trend Test (Numeric Time)

-   **Goal:** Demonstrate the simplest use case of the package: a standard Mann-Kendall and Sen's slope analysis on a simple, non-seasonal dataset with a numeric time vector.
-   **Dataset:** A small, synthetically generated dataset with a clear linear trend and some random noise. The time vector will be a simple integer sequence (e.g., `np.arange(n)`).
-   **Key Functions & Parameters:**
    -   `MannKenSen.trend_test()`
    -   Basic interpretation of the output tuple (p-value, slope, trend classification).

---

### Example 2: Non-Seasonal Trend Test with Timestamps

-   **Goal:** Introduce the handling of real-world time series data using `pandas` `datetime` objects.
-   **Dataset:** A synthetic dataset spanning several years with monthly observations and a clear trend. The time vector will be a `pandas.date_range`.
-   **Key Functions & Parameters:**
    -   `MannKenSen.trend_test()`
    -   Demonstrate how the package automatically handles `datetime` inputs.
    -   Introduce the `plot_path` parameter to generate and save a visualization of the trend.

---

### Example 3: Handling Censored Data

-   **Goal:** Explain and demonstrate the workflow for analyzing a dataset containing censored data points.
-   **Dataset:** A synthetic dataset similar to Example 2, but with some values represented as censored strings (e.g., `'<5'`, `'>50'`).
-   **Key Functions & Parameters:**
    -   `MannKenSen.prepare_censored_data()`: Show how to pre-process raw data into the required format.
    -   `MannKenSen.trend_test()`: Run the trend test on the processed data.
    -   `plot_path`: Visualize the trend with censored data points highlighted.

---

### Example 4: Basic Seasonal Trend Test

-   **Goal:** Introduce the concept of seasonal trend analysis.
-   **Dataset:** A synthetic dataset with a clear seasonal pattern (e.g., higher in summer, lower in winter) and an underlying linear trend across years.
-   **Key Functions & Parameters:**
    -   `MannKenSen.check_seasonality()`: Show how to statistically test for the presence of seasonality.
    -   `MannKenSen.seasonal_trend_test()`: Run the seasonal analysis.
    -   `period=12`: Explain the `period` parameter for monthly data.

---

### Example 5: Advanced Aggregation and LWP Compatibility

-   **Goal:** Demonstrate the powerful aggregation features and how to use them to handle clustered data and replicate the LWP-TRENDS R script's methodology.
-   **Dataset:** A synthetic dataset with an irregular sampling frequency (e.g., daily samples in one month, followed by monthly samples for the rest of the year).
-   **Analysis & Comparison:**
    1.  Run `MannKenSen.trend_test()` with `agg_method='none'` to show how the high-density data cluster can bias the Sen's slope.
    2.  Run `MannKenSen.trend_test()` with `agg_method='lwp'` and `agg_period='month'` to show how temporal aggregation mitigates this bias.
    3.  Explain the use of other compatibility flags (`sens_slope_method='lwp'`, `mk_test_method='lwp'`, `ci_method='lwp'`) for users who need to validate results against the LWP R script.

---

### Example 6: Interpreting Confidence and Classification

-   **Goal:** Provide a deeper dive into the interpretation of the statistical outputs, particularly the trend classification.
-   **Dataset:** A synthetic dataset with a weak or ambiguous trend.
-   **Key Functions & Parameters:**
    -   `MannKenSen.trend_test()`
    -   `alpha`: Demonstrate how changing the significance level (`alpha`) can change the `h` (significance) and `classification` results.
    -   `category_map`: Show how to provide a custom dictionary to the `category_map` parameter to define custom classification labels.
    -   Explain the meaning of `C` (Confidence) and how it relates to the final classification.

---

### Example 7: Regional Trend Analysis

-   **Goal:** Demonstrate how to aggregate trend results from multiple sites to determine a regional trend.
-   **Dataset:** A set of 3-4 synthetic time series, where some show an increasing trend, some a decreasing trend, and some no trend.
-   **Key Functions & Parameters:**
    -   `MannKenSen.trend_test()`: Run on each site individually.
    -   `MannKenSen.regional_test()`: Pass the results of the individual tests to this function.
    -   Explain the interpretation of the regional test output, including the aggregate trend strength (`TAU`) and direction (`DT`).
