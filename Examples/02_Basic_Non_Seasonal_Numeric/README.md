# Example 2: Basic Non-Seasonal Trend Test (Numeric Time)

### Goal

This example demonstrates the simplest and most fundamental use case of the `MannKenSen` package: performing a non-seasonal Mann-Kendall and Sen's slope analysis on a dataset with a simple numeric time vector. This is a common scenario for annual summary data or when the time component is represented by simple indices.

### Python Script (`run_example.py`)

The script below generates a synthetic dataset with 50 data points. The time vector is a simple integer sequence from 0 to 49. The values have a clear upward trend (a true slope of 0.1) with some random noise added. It then calls `MannKenSen.trend_test()` and prints the key results.

```python
import numpy as np
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# This example demonstrates the simplest use case: a non-seasonal trend test
# on a dataset with a simple numeric time vector.
np.random.seed(42)
n_samples = 50
time = np.arange(n_samples)

# Create data with a clear upward trend (slope of approx. 0.1) and add noise
trend = 0.1 * time
noise = np.random.normal(0, 0.5, n_samples)
values = trend + noise

# --- 2. Perform the Trend Test ---
# Call the trend_test function with the data.
# Since the data is not censored, we don't need to pre-process it.
result = mks.trend_test(x=values, t=time)

# --- 3. Print and Interpret the Results ---
print("--- MannKenSen Trend Analysis Results ---")
print(f"Trend Classification: {result.classification}")
print(f"Is Trend Significant? (h): {result.h}")
print(f"P-value (p): {result.p:.4f}")
print(f"Sen's Slope: {result.slope:.4f}")
print(f"Intercept: {result.intercept:.4f}")
print(f"95% Confidence Intervals: [{result.lower_ci:.4f}, {result.upper_ci:.4f}]")
print(f"Mann-Kendall Score (s): {result.s}")
print(f"Kendall's Tau: {result.Tau:.4f}")

```

### Results and Interpretation

Running the script produces the following output:

```
--- MannKenSen Trend Analysis Results ---
Trend Classification: Highly Likely Increasing
Is Trend Significant? (h): True
P-value (p): 0.0000
Sen's Slope: 0.0938
Intercept: 0.0681
95% Confidence Intervals: [0.0841, 0.1035]
Mann-Kendall Score (s): 983.0
Kendall's Tau: 0.8024
```

#### Interpretation:

-   **Trend Classification & Significance:** The output `Highly Likely Increasing` and `Is Trend Significant? (h): True` immediately tell us that the test found a statistically significant upward trend.
-   **P-value (p):** The p-value of `0.0000` (which is a rounded value, meaning p < 0.0001) confirms this. It is far below the default significance level (`alpha=0.05`), providing strong evidence against the null hypothesis of "no trend".
-   **Sen's Slope:** The calculated Sen's Slope is `0.0938`. This is the robust, non-parametric estimate of the trend's magnitude. It is very close to our true synthetic slope of 0.1, indicating the test accurately captured the underlying trend.
-   **Confidence Intervals:** The 95% confidence intervals for the slope are `[0.0841, 0.1035]`. This means we are 95% confident that the true slope of the trend lies within this range. Since this range does not include 0 and contains our true slope of 0.1, it further strengthens our conclusion of a significant increasing trend.
-   **Kendall's Tau:** The value of `0.8024` indicates a very strong positive correlation between the data and time, which is consistent with a strong upward trend.
