
# Example 18: Standalone Trend Classification

A powerful feature of the `MannKenSen` package is the ability to re-evaluate the trend classification using a custom scheme *without* re-running the full statistical analysis. The `MannKenSen.classify_trend()` function can be used on any result object returned by `trend_test`.

This is useful for applying custom, user-defined classification schemes based on confidence levels.

## The Python Script

The following script demonstrates two key concepts:
1.  How the `alpha` (significance level) chosen during the `trend_test` call affects the default classification.
2.  How to use the standalone `classify_trend` function with a `category_map` to apply a custom classification to an existing result.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks

# 1. Generate data with a borderline trend (p-value between 0.05 and 0.1)
np.random.seed(10)
n = 30
t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='YE'))
x = np.linspace(0, 2, n) + np.random.normal(0, 2.0, n) # Increased noise

# 2. Run the test with a lenient alpha=0.1
print("--- Analysis with alpha=0.1 ---")
result_lenient = mks.trend_test(x, t, alpha=0.1)
print(f"P-value: {result_lenient.p:.4f}")
print(f"Classification: {result_lenient.classification}")


# 3. Run the test again with a stricter alpha=0.05
print("\n--- Analysis with alpha=0.05 ---")
result_strict = mks.trend_test(x, t, alpha=0.05)
print(f"P-value: {result_strict.p:.4f}")
print(f"Classification: {result_strict.classification}")


# 4. Re-classify the original result with a custom map
print("\n--- Standalone Classification with Custom Map ---")
custom_map = {
    0.0: "Weak Trend",
    0.90: "Moderate Trend",
    0.95: "Strong Trend",
}
# We use the result from the first test for this demonstration
classification_custom = mks.classify_trend(result_lenient, category_map=custom_map)
print(f"Custom Classification: {classification_custom}")

```

## Command Output

Running the script produces the following output:

```
--- Analysis with alpha=0.1 ---
P-value: 0.0540
Classification: Highly Likely Increasing

--- Analysis with alpha=0.05 ---
P-value: 0.0540
Classification: No Trend

--- Standalone Classification with Custom Map ---
Custom Classification: Strong Trend Increasing
```

## Interpretation of Results

### The Effect of `alpha`

The p-value of the analysis is **0.0540**.
-   When we run the test with `alpha=0.1`, the p-value (0.0540) is less than alpha, so the trend is considered statistically significant, resulting in a classification of **'Highly Likely Increasing'**.
-   When we run the test with a stricter `alpha=0.05`, the p-value (0.0540) is now *greater* than alpha, so the trend is **not** considered statistically significant, resulting in a classification of **'No Trend'**.

This perfectly demonstrates how the choice of significance level impacts the final interpretation.

### Standalone Classification with a Custom Map

The true power of the standalone `classify_trend` function is in applying a completely different classification scheme. Here, we take our original result object (where the confidence `C` is `0.973`) and apply our custom map.

Since `0.973` is greater than the `0.95` threshold in our map, the trend is classified as a **'Strong Trend Increasing'**, demonstrating how you can separate the statistical calculation from your own domain-specific interpretation.
