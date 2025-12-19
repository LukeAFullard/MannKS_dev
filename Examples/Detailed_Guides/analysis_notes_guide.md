
# A Comprehensive Guide to Analysis Notes

The `MannKenSen` package includes a system of "Analysis Notes" to provide data quality warnings. These notes do not stop the analysis, but they alert you to potential issues in your dataset that could affect the reliability of the trend results. This guide explains what each note means, what triggers it, and what actions you can take.

---

### `< 3 unique values`
-   **What it means:** There are fewer than 3 unique, non-censored values in your dataset.
-   **What triggers it:** Data like `[1, 1, 2, 2, 1, 1, 2, 2]`.
-   **What to do:** A trend analysis is not meaningful with such low variability. This note usually indicates an issue with your data query or that the data is not suitable for trend analysis.

---

### `< 5 Non-censored values`
-   **What it means:** There are fewer than 5 non-censored data points available for the analysis.
-   **What triggers it:** A very small dataset, or a larger dataset where most of the values are censored (e.g., `['<1', '<1', '<1', 5, 6, 7]`).
-   **What to do:** The statistical power of the test is too low with such a small sample size. You should be very cautious about interpreting the results. The trend, if any, is unlikely to be statistically significant.

---

### `Long run of single value`
-   **What it means:** A significant portion of your data (by default, >50%) consists of a single, repeated value.
-   **What triggers it:** Data with a high number of ties, such as `[1, 2, 3, 3, 3, 3, 3, 3, 4, 5]`.
-   **What to do:** This is a strong indicator of tied data, which can reduce the power of the Mann-Kendall test. While the test is designed to handle ties, an excessive number can still be problematic. Ensure this is not due to a data quality issue.

---

### `tied timestamps present without aggregation`
-   **What it means:** Your time vector `t` contains duplicate values, and you have not specified an aggregation method.
-   **What triggers it:** Data where multiple measurements were recorded at the exact same time.
-   **What to do:** This is a critical warning. The Sen's slope calculation is sensitive to this and the result may be biased. **It is highly recommended to use an aggregation method.** See [Example 8](./08_Aggregation_Tied_Clustered_Data/README.md) for a detailed guide on how to use `agg_method` to resolve this.

---

### `WARNING: Sen slope influenced by [left/right]-censored values.`
-   **What it means:** The median Sen's slope (the final reported slope) was calculated from a pair of data points where at least one of the points was censored.
-   **What triggers it:** This is common in datasets with a moderate to high amount of censoring. It happens when the median of all the pairwise slopes happens to be a slope calculated from a pair involving a censored value.
-   **What to do:** This is an advisory note. It reminds you that the magnitude of your Sen's slope is an **estimate** that depends on the `lt_mult` or `gt_mult` parameters used for the calculation. You can perform a sensitivity analysis by re-running the test with different multipliers to see how much the slope changes. See [Example 12](./12_Censored_Data_Multipliers/README.md) for details.

---

### `sample size (X) below minimum (Y)`
-   **What it means:** The number of data points in your dataset is below the recommended minimum size.
-   **What triggers it:** By default, `min_size` is 10. If you provide fewer than 10 data points, this note will be generated.
-   **What to do:** Be cautious. The results from a small dataset may not be reliable. You can change the threshold by setting the `min_size` parameter in the `trend_test` function if you have a specific reason to analyze a smaller dataset. See [Example 25](./25_advanced_parameter_nuances/README.md) for more.

---

### `CRITICAL: Sen slope is based on a pair of two censored values.`
-   **What it means:** The median Sen's slope was calculated from a pair of two censored values (e.g., the slope between `<5` and `<10`).
-   **What triggers it:** This is rare, but can happen in heavily censored datasets where there are very few uncensored values.
-   **What to do:** Treat the Sen's slope result with **extreme caution**. Its value is highly dependent on the `lt_mult` and `gt_mult` parameters and may not be a reliable indicator of the true trend magnitude.
