
# A Comprehensive Guide to Trend Classification

The `MannKenSen` package provides a sophisticated trend classification system to help you interpret the results of a trend analysis. This guide explains how the classification works, what the different categories mean, and how you can customize them.

The classification is performed by the `classify_trend` function, which is automatically called by `trend_test` and `seasonal_trend_test`.

---

### How Classification Works

The classification depends on three key outputs from the trend test:

1.  **P-value (`p`):** The probability of observing the trend by chance. A low p-value (e.g., < 0.05) means the trend is statistically significant.
2.  **Sen's Slope (`slope`):** The magnitude and direction of the trend. A positive slope is an increasing trend, and a negative slope is a decreasing trend.
3.  **Confidence (`C`):** A measure of confidence in the trend's direction, ranging from 0 to 1. It is calculated as `1 - p`.

The system uses these three values to assign a trend classification based on a set of confidence categories.

---

### The Default Confidence Categories

By default, the package uses a classification scheme inspired by the Intergovernmental Panel on Climate Change (IPCC). It maps confidence levels to descriptive categories:

| Confidence (`C`) | P-value (`p`) | Trend Category         |
| :--------------- | :------------ | :--------------------- |
| `C >= 0.95`      | `p <= 0.05`   | **Increasing/Decreasing** |
| `0.90 <= C < 0.95` | `0.05 < p <= 0.10` | **Likely Increasing/Decreasing** |
| `0.67 <= C < 0.90` | `0.10 < p <= 0.33` | **Probably Increasing/Decreasing** |
| `0.33 <= C < 0.67` | `0.33 < p <= 0.67` | **No Clear Trend**         |
| `C < 0.33`       | `p > 0.67`    | **Stable**             |

-   **Increasing/Decreasing:** High confidence. There is a statistically significant trend.
-   **Likely...:** Medium-high confidence. The trend is close to being significant.
-   **Probably...:** Medium-low confidence. There is some evidence of a trend, but it is weak.
-   **No Clear Trend:** The evidence is ambiguous. The trend is not statistically significant.
-   **Stable:** High confidence that there is *no* trend. The p-value is very high, indicating the data is close to random.

**Note:** The `alpha` parameter you provide to `trend_test` (default is `0.05`) directly defines the threshold for the highest confidence category.

See **[Example 16: Trend Classification](./16_Trend_Classification/README.md)** for a practical demonstration of these categories.

---

### Customizing the Classification

You may have different requirements for trend classification. The `classify_trend` function (and by extension, the main test functions) accepts a `category_map` parameter to let you define your own rules.

The `category_map` is a dictionary where keys are the category names and values are the **minimum confidence level** required for that category.

For example, a simpler, stricter classification system could be:

```python
my_map = {
    "Significant": 0.95,  # Confidence >= 0.95 (p <= 0.05)
    "Suggestive": 0.90,   # Confidence >= 0.90 (p <= 0.10)
    "Indeterminate": 0.0, # All other cases
}
```

You would then pass this to the test function:

```python
result = mks.trend_test(..., category_map=my_map)
print(result.trend)
```

**Key Rules for Custom Maps:**

1.  The values must be confidence levels (between 0 and 1).
2.  The function will find the highest confidence threshold that the result's confidence (`C`) meets or exceeds.
3.  You must include a "zero" threshold (e.g., `"Indeterminate": 0.0`) to act as a catch-all for results that do not meet any other criteria.

See **[Example 17: Custom Trend Classification](./17_Custom_Trend_Classification/README.md)** for a hands-on guide to creating and using custom maps.
