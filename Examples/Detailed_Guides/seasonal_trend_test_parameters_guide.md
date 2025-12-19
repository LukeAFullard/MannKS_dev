
# A Comprehensive Guide to `seasonal_trend_test` Parameters

The `seasonal_trend_test` function is designed to perform a Mann-Kendall trend test on data with seasonal cycles. It extends the `trend_test` function with parameters to handle seasonality. This guide provides a detailed explanation of each parameter.

---

### Core Parameters

These are the essential parameters you will always need to provide.

#### `x`
-   **Type:** `numpy.ndarray` or `pandas.DataFrame`
-   **Description:** This is your primary data vector containing the observations. It can be a simple NumPy array or a pandas DataFrame pre-processed by `prepare_censored_data`, which is required if your data is censored.

#### `t`
-   **Type:** `numpy.ndarray`
-   **Description:** This is the time vector corresponding to your `x` values. It can contain numeric values (like years) or datetime objects. The function will use this vector to determine the season and year for each data point.

#### `alpha`
-   **Type:** `float`
-   **Default:** `0.05`
-   **Description:** The statistical significance level for the Mann-Kendall test. A value of `0.05` corresponds to a 95% confidence level.

#### `plot_path`
-   **Type:** `str` (optional)
-   **Default:** `None`
-   **Description:** If you provide a file path (e.g., `"seasonal_plot.png"`), the function will generate and save a plot visualizing the overall trend analysis.

---

### Seasonality Parameters

These parameters are crucial for defining the seasonal structure of your data.

#### `period`
-   **Type:** `int`
-   **Default:** `12`
-   **Description:** This defines the length of a full seasonal cycle. For monthly data, the default of `12` is appropriate. For quarterly data, you would use `4`. This parameter is primarily used when your time vector `t` is numeric. If you are using datetime objects, the `season_type` parameter is often more convenient.

#### `season_type`
-   **Type:** `str`
-   **Default:** `'month'`
-   **Description:** When your time vector `t` consists of datetime objects, this parameter specifies how to define the seasons. The options are highly flexible:
    -   `'month'`: For standard monthly seasonality.
    -   `'quarter'`: For quarterly data.
    -   `'week_of_year'`: For weekly patterns (period would be 52/53).
    -   `'day_of_year'`: For daily patterns within a year (period 365/366).
    -   `'day_of_week'`: For weekly cycles (e.g., Monday-Sunday, period 7).
    -   And more granular options like `'hour'`, `'minute'`, and `'second'`.
    See **[Example 11: Advanced Seasonality](./11_Advanced_Seasonality/README.md)**.

---

### Aggregation Parameters

These parameters control how to handle multiple observations that fall within the same season and the same year (or cycle).

#### `agg_method`
-   **Type:** `str`
-   **Default:** `'none'`
-   **Options:** `'none'`, `'median'`, `'robust_median'`, `'middle'`, `'middle_lwp'`, `'lwp'`
-   **Description:** This determines the method for reducing multiple data points in the same season-cycle block to a single point.
    -   `'none'`: The test is performed on all data, which is generally appropriate if you have only one observation per season per year.
    -   `'lwp'` / `'median'`: These methods are provided for compatibility with the LWP-TRENDS R script, which aggregates data before analysis.
    -   `'robust_median'`: This is the recommended aggregation method if you have censored data, though it should still be used with caution as aggregating censored data can introduce bias.
    See **[Example 8](./08_Aggregation_Tied_Clustered_Data/README.md)** for a general discussion on aggregation.

---

### Censored Data Parameters

These parameters are identical to their counterparts in `trend_test`.

#### `hicensor`
-   **Type:** `bool` or `float`
-   **Default:** `False`
-   **Description:** Activates the "high censor" rule to mitigate the effect of improving detection limits.

#### `lt_mult` and `gt_mult`
-   **Type:** `float`
-   **Defaults:** `lt_mult=0.5`, `gt_mult=1.1`
-   **Description:** Multipliers used for calculating Sen's slope with censored data. They do not affect the Mann-Kendall test itself.

#### `sens_slope_method`
-   **Type:** `str`
-   **Default:** `'nan'`
-   **Options:** `'nan'`, `'lwp'`
-   **Description:** Controls how slopes between two censored points are handled. `'nan'` is the recommended, neutral approach.

#### `mk_test_method`
-   **Type:** `str`
-   **Default:** `'robust'`
-   **Options:** `'robust'`, `'lwp'`
-   **Description:** Controls how the Mann-Kendall test handles right-censored data (`>`). `'robust'` is the recommended statistical method.

---

### Advanced Statistical Parameters

These are for advanced users and are identical to their counterparts in `trend_test`.

#### `tau_method`
-   **Type:** `str`
-   **Default:** `'b'`
-   **Options:** `'a'`, `'b'`
-   **Description:** Use `'b'` (default) to account for ties in the data.

#### `ci_method`
-   **Type:** `str`
-   **Default:** `'direct'`
-   **Options:** `'direct'`, `'lwp'`
-   **Description:** Controls the method for calculating Sen's slope confidence intervals.

---

### Other Parameters

#### `min_size_per_season`
-   **Type:** `int` (optional)
-   **Default:** `5`
-   **Description:** The minimum number of observations required for a season to be included in the analysis. If any season has fewer data points than this value, an "analysis note" warning will be generated. You can set it to `None` to disable the check.

#### `category_map`
-   **Type:** `dict` (optional)
-   **Default:** `None`
-   **Description:** Allows you to provide your own custom rules for trend classification. If not provided, a default IPCC-inspired classification scheme is used. See our **[Trend Classification Guide](./trend_classification_guide.md)** for a full explanation.
