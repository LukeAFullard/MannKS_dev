# A Comprehensive Guide to Trend Classification

The `MannKenSen` package provides a sophisticated trend classification system to help you interpret the results of a trend analysis. This guide explains how the classification works, what the different categories mean, their uses and limitations, and how you can customize them.

The classification is performed by the `classify_trend` function, which is automatically called by `trend_test` and `seasonal_trend_test`.

---

### How Classification Works: The Three Key Ingredients

The classification system is designed to translate complex statistical results into a simple, human-readable label. It does this using three key pieces of information from the trend test:

1.  **P-value (`p`):**
    -   **What it is:** In simple terms, the p-value is the probability of seeing your data, or something more extreme, *purely by random chance*, assuming that no real trend actually exists.
    -   **How to think about it:** Imagine you see a trend in your data. A low p-value (e.g., `p < 0.05`) is like saying, "It's very unlikely we'd see a trend this strong just by accident." This gives us confidence that the trend is real. A high p-value suggests the observed pattern could easily be random noise.

2.  **Sen's Slope (`slope`):**
    -   **What it is:** This is the magnitude and direction of the trend. It is a robust estimate, calculated as the median of the slopes between all pairs of points in your data.
    -   **How to think about it:** A positive slope means an increasing trend (e.g., "+2 units per year"), and a negative slope means a decreasing trend ("-5 units per year"). The classification system uses the sign of the slope to determine if a trend is "Increasing" or "Decreasing".

3.  **Confidence (`C`):**
    -   **What it is:** This is a more intuitive measure of confidence in the trend's direction, calculated as `C = 1 - p`. It ranges from 0 to 1.
    -   **How to think about it:** A p-value of `0.05` corresponds to a confidence of `0.95` (or 95%). This value is easier to work with for setting classification thresholds.

The system uses the **Confidence (`C`)** to determine the category and the **Slope** to determine the direction.

---

### The Default Confidence Categories

By default, the package uses a classification scheme inspired by the Intergovernmental Panel on Climate Change (IPCC) to provide a nuanced interpretation.

| Confidence (`C`) | P-value (`p`) | Trend Category         | Interpretation |
| :--------------- | :------------ | :--------------------- | :--- |
| `C >= 0.95`      | `p <= 0.05`   | **Increasing/Decreasing** | High confidence. The trend is statistically significant. |
| `0.90 <= C < 0.95` | `0.05 < p <= 0.10` | **Likely Increasing/Decreasing** | Medium-high confidence. The trend is borderline significant. |
| `0.67 <= C < 0.90` | `0.10 < p <= 0.33` | **Probably Increasing/Decreasing** | Medium-low confidence. Some evidence of a trend, but it is weak. |
| `0.33 <= C < 0.67` | `0.33 < p <= 0.67` | **No Clear Trend**         | Ambiguous. We lack enough evidence to determine a trend direction. |
| `C < 0.33`       | `p > 0.67`    | **Stable**             | High confidence that there is *no* meaningful trend. |

-   **Increasing/Decreasing:** This is the strongest conclusion. There is a clear, statistically significant trend.
-   **Likely...:** Often used in scientific reporting to indicate a result that is meaningful but just misses the traditional significance cutoff.
-   **Probably...:** There's a hint of a trend, but it's not strong. This could be a real but very slight trend, or it could be noise.
-   **No Clear Trend:** This is a statement about **evidence**. It does *not* mean there is no trend; it means the data does not provide enough evidence to confidently state that a trend exists in either direction.
-   **Stable:** This is different from "No Clear Trend". A very high p-value provides strong evidence that the data is close to random, giving us confidence that there is no underlying trend.

**Note:** The `alpha` parameter you provide to `trend_test` (default is `0.05`) directly defines the threshold for the highest confidence category (`Increasing/Decreasing`).

### Usefulness and Limitations of Classification

-   **Usefulness:** Classification is extremely useful for **summarization**. If you are analyzing hundreds of sites, a table of trend categories gives you an immediate overview. It also provides a standardized vocabulary for reporting results.
-   **Limitations:** A category is a **simplification**. A p-value of `0.049` ("Increasing") and `0.051` ("Likely Increasing") are statistically almost identical, but they fall into different categories. **Never rely only on the category.** Always inspect the p-value and the Sen's slope magnitude to understand the full picture.

---

### Customizing the Classification

You can define your own classification rules using the `category_map` parameter. This is a dictionary where keys are the category names and values are the **minimum confidence level (`C`)** required.

For example, a simpler, stricter classification system could be:
```python
my_map = {
    "Significant": 0.95,  # Confidence >= 0.95 (p <= 0.05)
    "Suggestive": 0.90,   # Confidence >= 0.90 (p <= 0.10)
    "Indeterminate": 0.0, # All other cases (the catch-all)
}
```
You would pass this to the test function: `mks.trend_test(..., category_map=my_map)`

**Key Rules for Custom Maps:**
1.  The values are confidence levels (`1 - p`), from 0 to 1.
2.  The function finds the category with the highest minimum confidence that your result still meets or exceeds.
3.  You **must** include a "zero" threshold (e.g., `"Indeterminate": 0.0`) to act as a catch-all for results that don't meet any other criteria.
