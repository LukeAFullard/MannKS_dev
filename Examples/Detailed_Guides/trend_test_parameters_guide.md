# A Comprehensive Guide to `trend_test` Parameters

The `trend_test` function is the workhorse for non-seasonal trend analysis in the `MannKenSen` package. It has a rich set of parameters that allow you to fine-tune the analysis to your specific needs. This guide provides a detailed explanation of each parameter, including its purpose, usefulness, and limitations.

---

### Core Parameters

These are the essential parameters you will always need to provide.

#### `x`
-   **Type:** `numpy.ndarray` or `pandas.DataFrame`
-   **Description:** This is your primary data vector containing the observations.
-   **Usefulness and Nuances:** If your data is purely numeric, a simple NumPy array is sufficient. If you have censored data (e.g., `"<5"`), you **must** pre-process it first using the `prepare_censored_data` function and provide the resulting DataFrame here.

#### `t`
-   **Type:** `numpy.ndarray`
-   **Description:** This is the time vector corresponding to your `x` values. The values in `t` must correspond one-to-one with the values in `x`.
-   **Usefulness and Nuances:** The key feature of `MannKenSen` is its ability to handle unequally spaced timestamps. `t` can contain numeric values (e.g., `2001.5`, `2002.75`) or, more commonly, datetime objects. The function automatically handles the conversion of datetimes for calculations.

#### `alpha`
-   **Type:** `float`, **Default:** `0.05`
-   **Description:** The statistical significance level. It's the threshold for deciding if a trend is statistically significant.
-   **Usefulness and Limitations:** An `alpha` of `0.05` corresponds to a 95% confidence level, a common standard in many scientific fields. Setting a lower `alpha` (e.g., `0.01`) makes the test stricter, reducing the risk of a "false positive" (detecting a trend that isn't real). However, this increases the risk of a "false negative" (missing a real but weak trend). The choice of `alpha` depends on the standards of your field and how you want to balance these risks.

#### `plot_path`
-   **Type:** `str` (optional), **Default:** `None`
-   **Description:** If you provide a file path (e.g., `"my_trend_plot.png"`), the function will save a plot visualizing the trend analysis.
-   **Usefulness:** This is extremely useful for diagnostics. A plot can help you visually assess the trend, identify potential outliers, and understand the relationship between the data, the Sen's slope, and the confidence intervals.

---

### Censored Data Parameters

These parameters control how the test handles censored data.

#### `hicensor`
-   **Type:** `bool` or `float`, **Default:** `False`
-   **Description:** Activates the "high censor" rule, a conservative method to handle improving detection limits over time.
-   **Usefulness:** Imagine your detection limit improved from `<10` in the 1990s to `<1` in the 2010s. An actual concentration of `3` would be recorded as `<10` in 1995 but `3` in 2015. This can create a misleading "increasing" trend. `hicensor=True` mitigates this by treating all values (censored or not) below the highest detection limit (`10` in this case) as being censored at that high limit. This provides a more conservative and potentially more accurate assessment of the true underlying trend.
-   **Limitations:** By being conservative, this rule can sometimes mask a real but weak trend. It is most appropriate when you have a clear history of changing detection limits. See **[Example 8](./08_High_Censor_Rule/README.md)**.

#### `lt_mult` and `gt_mult`
-   **Type:** `float`, **Defaults:** `lt_mult=0.5`, `gt_mult=1.1`
-   **Description:** Multipliers used to substitute censored values **only for the Sen's slope calculation**. They do **not** affect the p-value or trend significance.
-   **Usefulness and Nuances:** To calculate a slope, you need two numbers. A value like `"<10"` is temporarily replaced by `10 * 0.5 = 5`. The default `lt_mult=0.5` is chosen because it's the midpoint of the possible range `[0, 10]`, representing a neutral estimate. `gt_mult=1.1` is used to place the substituted value slightly outside the uncensored range. These parameters allow you to perform a sensitivity analysis by seeing how the slope magnitude changes with different multipliers.
-   **Limitations:** This is a simple substitution, not a statistical model like Regression on Order Statistics (ROS). The resulting slope is an estimate whose accuracy depends on how well the multiplier reflects the true underlying values. See **[Example 13](./13_Censored_Data_Multipliers/README.md)**.

#### `sens_slope_method`
-   **Type:** `str`, **Default:** `'nan'`
-   **Description:** Controls how to handle the ambiguous case of calculating a slope between two censored points.
-   **Usefulness:** A slope between `<5` and `<10` is ambiguous. The default `'nan'` treats this slope as unknown and excludes it from the final median calculation. This is the most statistically neutral and recommended approach. The `'lwp'` option sets these ambiguous slopes to `0`, which is provided for reproducibility against an older R script.
-   **Limitations:** The `'lwp'` method can bias the final Sen's slope towards zero, especially in heavily censored datasets. It should be used with caution. See **[Example 21](./21_Sens_Slope_Methods/README.md)**.

#### `mk_test_method`
-   **Type:** `str`, **Default:** `'robust'`
-   **Description:** Controls how the Mann-Kendall test ranks right-censored data (`>`).
-   **Usefulness:** The default `'robust'` method uses a statistically sound approach where a value like `>100` is treated as having a rank higher than any value below 100, but its exact rank relative to other right-censored values is handled by specific tie-correction rules. The `'lwp'` method uses a simpler heuristic that replaces all `>` values with a single number slightly larger than the max uncensored value. This is less robust but is provided for compatibility with the LWP-TRENDS script.
-   **Limitations:** The `'lwp'` heuristic can be sensitive to outliers and is generally not recommended unless direct comparison to that specific script is the primary goal. See **[Example 10](./10_Right_Censored_Methods/README.md)**.

---

### Aggregation Parameters

#### `agg_method`
-   **Type:** `str`, **Default:** `'none'`
-   **Description:** Determines how to handle multiple observations that occur at the same time or within the same time period.
-   **Usefulness:** This is critical for two scenarios:
    1.  **Tied Timestamps:** If you have multiple measurements for the exact same timestamp, you must aggregate them to avoid calculation errors.
    2.  **Clustered Data:** If you have high-frequency data (e.g., daily samples for one month, then monthly for years), it can bias the trend result. The `'lwp'` method, used with `agg_period`, aggregates all data within a period (e.g., a year) to a single point, ensuring each period has equal weight.
-   **Limitations:** Aggregation, by definition, reduces the amount of data used in the test, which can lower its statistical power. For censored data, `'robust_median'` is the recommended method, but be aware that aggregating censored values is a difficult statistical problem and the result should be interpreted with care. See **[Example 9](./09_Aggregation_Tied_Clustered_Data/README.md)**.

#### `agg_period`
-   **Type:** `str`, **Default:** `'year'`
-   **Description:** Defines the time window for aggregation **only when `agg_method='lwp'`**.
-   **Usefulness:** This allows you to define the granularity of your analysis whendealing with clustered data. You can analyze trends on an aggregated `'year'`, `'month'`, or `'day'` basis. This requires that your time vector `t` contains datetime objects.

---

### Advanced Statistical Parameters

Defaults are recommended for most users.

#### `tau_method`
-   **Type:** `str`, **Default:** `'b'`
-   **Description:** Controls which version of Kendall's Tau is calculated.
-   **Usefulness:** Real-world data almost always contains "ties" (identical values). Tau-b (the default) is the standard modification that correctly handles ties. Tau-a does not and is generally only appropriate for theoretical, continuous data with no ties.

#### `ci_method`
-   **Type:** `str`, **Default:** `'direct'`
-   **Description:** Controls the method for calculating the Sen's slope confidence intervals.
-   **Usefulness:** The confidence interval gives you a range of plausible values for the true slope. The `'direct'` method is a standard, statistically robust approach. The `'lwp'` method uses a specific interpolation technique designed to replicate the LWP-TRENDS R script. Unless you need that specific replication, `'direct'` is recommended. See **[Example 14](./14_Confidence_Interval_Methods/README.md)**.

---

### Other Parameters

#### `min_size`
-   **Type:** `int`, **Default:** `10`
-   **Description:** The minimum sample size required to avoid an "analysis note" warning.
-   **Usefulness:** This serves as a guideline to prevent over-interpretation of results from very small datasets, which have low statistical power and may not be reliable.
-   **Limitations:** This is a heuristic, not a hard statistical rule. You can set it to a different value or `None` to disable it if the standards for your field of work differ.

#### `category_map`
-   **Type:** `dict` (optional), **Default:** `None`
-   **Description:** Allows you to provide your own rules for trend classification.
-   **Usefulness:** If your organization or project has a specific set of reporting standards (e.g., "Improving", "Degrading", "No Change"), you can use this to map the statistical results directly to your required terminology. See our **[Trend Classification Guide](./trend_classification_guide.md)** for a full explanation.

---

### Slope Scaling Parameters

These parameters make the Sen's slope output more intuitive and readable.

#### `x_unit`
-   **Type:** `str`, **Default:** `"units"`
-   **Description:** A string to describe the units of your data `x`.
-   **Usefulness:** This string is used to construct the final `slope_units` field in the output. For example, if you provide `x_unit="mg/L"`, the output units will be formatted like `"mg/L per year"`, making the result and any plots much clearer.

#### `slope_scaling`
-   **Type:** `str` (optional), **Default:** `None`
-   **Description:** Specifies the desired time unit for the Sen's slope.
-   **Usefulness:** This is a powerful convenience feature. When your time vector `t` is made of datetimes, the raw slope is calculated in units per second. By setting `slope_scaling="year"`, the function will automatically multiply the raw slope by the number of seconds in a year and return a value in "units per year".
-   **Valid Units:** `year`, `month`, `week`, `day`, `hour`, `minute`, `second`.
-   **Limitations:** This parameter **only works** when `t` is a datetime-like array. It has no effect and will raise a `UserWarning` if `t` is numeric, because the function cannot know the underlying unit of a numeric time vector. See **[Example 3](./03_Non_Seasonal_Timestamps/README.md)**.
