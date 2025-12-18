
# Example 18: Standalone Trend Classification

A powerful feature of the `MannKenSen` package is the ability to re-evaluate the trend classification using a custom scheme *without* re-running the full statistical analysis. The `MannKenSen.classify_trend()` function can be used on any result object returned by `trend_test` or `seasonal_trend_test`.

This is useful for applying custom, user-defined classification schemes based on confidence levels.

## 1. The Effect of `alpha` During Analysis

The significance level `alpha` is used during the `trend_test` call to determine the boolean `h` flag and the default classification. A different `alpha` requires a new test run.

First, we run a test with a lenient `alpha=0.1`.

```python
import numpy as np
import pandas as pd
import MannKenSen

# Generate data with a borderline trend (p-value between 0.05 and 0.1)
np.random.seed(10)
n = 30
t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='YE'))
x = np.linspace(0, 2, n) + np.random.normal(0, 2.0, n) # Increased noise

# Run the test once with alpha=0.1
result_lenient = MannKenSen.trend_test(x, t, alpha=0.1)
print(f"P-value: {result_lenient.p:.4f}")
print(f"Classification (alpha=0.1): {result_lenient.classification}")

# Run the test again with alpha=0.05
result_strict = MannKenSen.trend_test(x, t, alpha=0.05)
print(f"Classification (alpha=0.05): {result_strict.classification}")

```

**Results:**
- P-value: 0.0540
- Classification (alpha=0.1): Highly Likely Increasing
- Classification (alpha=0.05): No Trend

The p-value (0.0540) is less than 0.1 but greater than 0.05. As a result, the trend is considered **'Highly Likely Increasing'** with the lenient alpha but **'No Trend'** with the stricter alpha, perfectly demonstrating the effect of the significance level.

## 2. Re-classifying with a Custom Map

The standalone `classify_trend` function allows you to apply your own logic to an **existing result object** using a custom `category_map`.

The keys of the map must be `float` values representing the lower confidence bound for each category.

```python
# Define a custom classification map based on confidence (1 - p)
custom_map = {
    0.0: "Weak Trend",
    0.90: "Moderate Trend",
    0.95: "Strong Trend",
}

# Re-classify the original result using the custom map
classification_custom_map = MannKenSen.classify_trend(result_lenient, category_map=custom_map)

print(f"Custom Classification: {classification_custom_map}")
```
**Custom Classification:** Strong Trend Increasing

This shows how you can separate the statistical calculation from the final interpretation, applying your own domain-specific labels to the trend analysis results.
