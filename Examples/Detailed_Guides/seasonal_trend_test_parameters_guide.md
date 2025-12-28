# A Comprehensive Guide to `seasonal_trend_test` Parameters

The `seasonal_trend_test` function is designed to perform a Mann-Kendall trend test on data with seasonal cycles. It works by calculating the trend test for each season individually and then combining the results for an overall trend. This guide provides a detailed explanation of each parameter, with a focus on those specific to seasonal analysis.

*For parameters not covered in detail here (`hicensor`, `lt_mult`, `gt_mult`, `tau_method`, `ci_method`, `tie_break_method`, etc.), see the [**`trend_test` parameter guide**](./trend_test_parameters_guide.md) for a full explanation.*

---

### Core Parameters

These are the essential parameters you will always need to provide.

#### `x`, `t`, `alpha`, `plot_path`
These core parameters function identically to their counterparts in `trend_test`. `x` holds the data, `t` holds the corresponding time vector, `alpha` sets the significance level, and `plot_path` saves a visualization of the results.

---

### Seasonality Parameters

These parameters are crucial for defining the seasonal structure of your data. The goal is to correctly group your data into distinct seasons (like "January", "February", etc.) so the test can analyze them.

#### `period`
-   **Type:** `int`, **Default:** `12`
-   **Description:** This defines the length of a full seasonal cycle.
-   **Usefulness and Nuances:** This parameter is primarily used when your time vector `t` is **numeric**. For example, if your time data is `[2001, 2001.25, 2001.5, 2002, 2002.25, 2002.5]`, you would use `period=4` to specify quarterly data. The default of `12` is for monthly data where `t` might be integer months. **If you are using datetime objects in `t`, the `season_type` parameter is strongly recommended as it is more explicit and powerful.**

#### `season_type`
-   **Type:** `str`, **Default:** `'month'`
-   **Description:** When `t` contains datetime objects, this parameter specifies how to extract the seasonal component from each timestamp.
-   **Usefulness and Nuances:** This is the most flexible and common way to define seasons.
    -   `'month'` (default): For standard monthly seasonality (12 seasons).
    -   `'quarter'`: For quarterly data (4 seasons).
    -   `'day_of_week'`: For cycles within a week, like Monday vs. Tuesday (7 seasons).
    -   `'week_of_year'`: For weekly patterns across a year (52/53 seasons).
    -   `'day_of_year'`: For daily patterns across a year (365/366 seasons).
    The choice is critical: using `'day_of_year'` for data collected over five years means you are testing for a trend in Jan 1st across those five years, Jan 2nd across those five years, and so on. See **[Example 12: Advanced Seasonality](./12_Advanced_Seasonality/README.md)**.

---

### Aggregation Parameters

Aggregation in a seasonal context is about ensuring that you have **one representative value per season per cycle**. For example, one value for "January 2010", one for "January 2011", etc.

#### `agg_method`
-   **Type:** `str`, **Default:** `'none'`
-   **Description:** This determines the method for reducing multiple data points that fall within the same season-cycle block (e.g., all samples in "January 2010") to a single representative point.
-   **Usefulness and Implications:**
    -   **When is it needed?** If you have multiple samples for a specific season-year (e.g., two samples in Jan 2010), you must aggregate them. The seasonal test requires exactly one observation per season per cycle.
    -   `'none'`: Use this only if your data is already structured as one observation per season per cycle.
    -   `'lwp'`: Selects the single observation closest to the theoretical midpoint of the period (mimics LWP R script `UseMidObs=TRUE`).
    -   `'median'`: Calculates the median of all values within the season-cycle block. Equivalent to LWP R script `UseMidObs=FALSE`.
    -   `'robust_median'`: As above, but uses a robust median logic suitable for censored data.
    -   `'middle'`: Selects the observation whose timestamp is closest to the mean of the actual timestamps in that season-year group.
    -   `'middle_lwp'`: Selects the observation closest to the theoretical midpoint of the time period.
-   **Limitations:** **Aggregating censored data is statistically complex and can introduce bias.** For example, the median of `['<2', '5', '10']` is `5`, but the median of `['<2', '<5', '10']` is ambiguous. The `'robust_median'` method uses a reasonable heuristic, but you should be aware of this underlying uncertainty. See **[Example 9](./09_Aggregation_Tied_Clustered_Data/README.md)**.

---

### Censored Data Parameters

#### `sens_slope_method`
-   **Type:** `str`, **Default:** `'nan'`
-   **Description:** Controls the method used for calculating the Sen's slope.
-   **Usefulness:**
    *   `'nan'`: Standard method. Ambiguous slopes (between two incompatible censored values) are treated as missing.
    *   `'ats'`: Uses the **Seasonal Akritas-Theil-Sen** estimator. This calculates the overall slope by finding the value that zeroes the sum of the seasonal Kendall scores. It is the most robust method for seasonal censored data.
    *   `'lwp'`: Sets ambiguous slopes to 0 (legacy behavior).
-   **Limitations:** `'ats'` is computationally intensive and does not currently support confidence intervals or probability outputs for the *seasonal* test (returns `NaN` for these fields).

#### `hicensor`, `lt_mult`, `gt_mult`, `mk_test_method`
These parameters function identically to their `trend_test` counterparts but are applied at the **seasonal level**. For example, `hicensor` will be applied independently to the data for each season. This is important because different seasons may have different data characteristics or censoring levels.

---

### Other Parameters

#### `min_size_per_season`
-   **Type:** `int`, **Default:** `5`
-   **Description:** The minimum number of observations required for a season to be included in the overall analysis.
-   **Usefulness and Implications:** This is a crucial quality control check. A trend analysis for "January" based on only two data points is not reliable. This parameter ensures that every season included in the final combined test has a sufficient data record. If a season fails this check (e.g., you only have 4 measurements for "April"), it will be dropped from the analysis, and a warning will be issued.
-   **Limitations:** This can sometimes lead to a situation where your overall trend is based on a subset of seasons (e.g., only the summer months if winter data is sparse). This is statistically valid, but you must be clear in your interpretation that the result does not represent the excluded seasons.

#### `category_map`
-   **Type:** `dict` (optional), **Default:** `None`
-   **Description:** Allows you to provide your own custom rules for trend classification, applied to the final overall trend result.
-   **Usefulness:** Same as in `trend_test`, this allows you to align the output with specific reporting requirements. See our **[Trend Classification Guide](./trend_classification_guide.md)**.

---

### Slope Scaling Parameters

#### `x_unit` and `slope_scaling`
These parameters function identically to their counterparts in `trend_test`. They allow you to provide a unit for your data (`x_unit`) and specify a desired time unit for the final Sen's slope (`slope_scaling`), such as `'year'`. This is a powerful convenience feature that removes the need for manual slope conversion when working with datetime objects.

-   **Usefulness:** Automatically get an interpretable slope like "mg/L per year" directly in the output and on the plot.
-   **Limitations:** `slope_scaling` is only effective when your time vector `t` is datetime-like.

For a full explanation, please see the **[Slope Scaling Parameters section in the `trend_test` guide](./trend_test_parameters_guide.md#slope-scaling-parameters)**.
