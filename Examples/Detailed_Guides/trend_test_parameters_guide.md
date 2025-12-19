
# A Comprehensive Guide to `trend_test` Parameters

The `trend_test` function is the workhorse for non-seasonal trend analysis in the `MannKenSen` package. It has a rich set of parameters that allow you to fine-tune the analysis to your specific needs. This guide provides a detailed explanation of each parameter.

---

### Core Parameters

These are the essential parameters you will always need to provide.

#### `x`
-   **Type:** `numpy.ndarray` or `pandas.DataFrame`
-   **Description:** This is your primary data vector containing the observations or measurements you want to analyze. It can be a simple NumPy array of numbers, or it can be a pandas DataFrame that has been pre-processed by the `prepare_censored_data` function, which is required if your data contains censored values.

#### `t`
-   **Type:** `numpy.ndarray`
-   **Description:** This is the time vector corresponding to your `x` values. The values in `t` must correspond one-to-one with the values in `x`. The `MannKenSen` package is specifically designed to handle unequally spaced timestamps, so the intervals between your time points do not need to be regular. `t` can contain numeric values (like years) or datetime objects.

#### `alpha`
-   **Type:** `float`
-   **Default:** `0.05`
-   **Description:** This is the statistical significance level for the Mann-Kendall test. It defines the threshold for determining if a trend is statistically significant. A value of `0.05` means you are using a 95% confidence level. The p-value from the test will be compared against this `alpha` to determine the `h` (significant) flag in the results.

#### `plot_path`
-   **Type:** `str` (optional)
-   **Default:** `None`
-   **Description:** If you provide a file path (e.g., `"my_trend_plot.png"`), the function will generate and save a plot visualizing the trend analysis, including your data points, the Sen's slope, and the confidence intervals.

---

### Censored Data Parameters

These parameters control how the test handles censored data (e.g., values like `<5` or `>100`).

#### `hicensor`
-   **Type:** `bool` or `float`
-   **Default:** `False`
-   **Description:** This activates the "high censor" rule. If set to `True`, all values (both censored and uncensored) that are below the single highest left-censored detection limit in your dataset will be treated as if they were censored at that high limit. This is a conservative approach used to mitigate artificial trends that can appear when detection limits improve over time. You can also provide a specific numeric threshold. See **[Example 7](./07_High_Censor_Rule/README.md)**.

#### `lt_mult` and `gt_mult`
-   **Type:** `float`
-   **Defaults:** `lt_mult=0.5`, `gt_mult=1.1`
-   **Description:** These multipliers are used **only for the Sen's slope calculation** when censored data is present. To calculate a slope between a censored and an uncensored point, the censored value is temporarily substituted. A left-censored value (e.g., `<10`) is replaced by `10 * lt_mult`. A right-censored value (e.g., `>100`) is replaced by `100 * gt_mult`. These multipliers **do not** affect the Mann-Kendall test for significance (the p-value). See **[Example 12](./12_Censored_Data_Multipliers/README.md)**.

#### `sens_slope_method`
-   **Type:** `str`
-   **Default:** `'nan'`
-   **Options:** `'nan'`, `'lwp'`
-   **Description:** This controls how slopes between two censored points (an ambiguous case) are handled. The default, `'nan'`, treats these slopes as unknown (`np.nan`) and excludes them from the median calculation, which is the most statistically neutral approach. The `'lwp'` option sets these slopes to `0`, which mimics an older R script but may bias the final slope towards zero. See **[Example 20](./20_Sens_Slope_Methods/README.md)**.

#### `mk_test_method`
-   **Type:** `str`
-   **Default:** `'robust'`
-   **Options:** `'robust'`, `'lwp'`
-   **Description:** This controls how the Mann-Kendall test handles right-censored data (`>`). The `'robust'` method uses a statistically sound ranking approach. The `'lwp'` method uses a heuristic that replaces all right-censored values with a single value slightly larger than the maximum uncensored value; this is provided for compatibility with the LWP-TRENDS script. See **[Example 9](./09_Right_Censored_Methods/README.md)**.

---

### Aggregation Parameters

These parameters are for handling datasets with tied timestamps or high-frequency data clusters.

#### `agg_method`
-   **Type:** `str`
-   **Default:** `'none'`
-   **Options:** `'none'`, `'median'`, `'robust_median'`, `'middle'`, `'middle_lwp'`, `'lwp'`
-   **Description:** This determines if and how data points with identical timestamps are aggregated. The default `'none'` will not aggregate but will issue a warning. For censored data, `'robust_median'` is the recommended method. The `'lwp'` method is special; it aggregates data into time periods (defined by `agg_period`) to handle clustered data, not just tied timestamps. See **[Example 8](./08_Aggregation_Tied_Clustered_Data/README.md)**.

#### `agg_period`
-   **Type:** `str`
-   **Default:** `'year'`
-   **Description:** This parameter is **only used when `agg_method='lwp'`**. It defines the time window for the aggregation, such as `'year'`, `'month'`, or `'day'`. Requires that the time vector `t` contains datetime objects.

---

### Advanced Statistical Parameters

These parameters allow you to change the underlying statistical calculations. It is recommended to use the defaults unless you have a specific reason.

#### `tau_method`
-   **Type:** `str`
-   **Default:** `'b'`
-   **Options:** `'a'`, `'b'`
-   **Description:** Controls the calculation of Kendall's Tau. Tau-b (default) is a modification that accounts for tied values in your data and is generally recommended. Tau-a does not account for ties.

#### `ci_method`
-   **Type:** `str`
-   **Default:** `'direct'`
-   **Options:** `'direct'`, `'lwp'`
-   **Description:** Controls the method for calculating the confidence intervals of the Sen's slope. The `'direct'` method is a standard approach. The `'lwp'` method uses an interpolation technique to mimic the behavior of the LWP-TRENDS R script. See **[Example 13](./13_Confidence_Interval_Methods/README.md)**.

#### `tie_break_method`
-   **Type:** `str`
-   **Default:** `'robust'`
-   **Options:** `'robust'`, `'lwp'`
-   **Description:** Controls a very subtle part of the Mann-Kendall tie correction. The `'robust'` method is recommended. The `'lwp'` option is available for close replication of the LWP-TRENDS R script.

---

### Other Parameters

#### `min_size`
-   **Type:** `int` (optional)
-   **Default:** `10`
-   **Description:** The minimum sample size required for the analysis. If the number of data points is below this value, an "analysis note" will be generated. You can set this to `None` to disable the check.

#### `category_map`
-   **Type:** `dict` (optional)
-   **Default:** `None`
-   **Description:** Allows you to provide your own custom rules for trend classification. If not provided, a default IPCC-inspired classification scheme is used. See our **[Trend Classification Guide](./trend_classification_guide.md)** for a full explanation.
