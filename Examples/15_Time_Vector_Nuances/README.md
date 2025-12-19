
# Example 14: Time Vector Nuances (Numeric Data)

This example highlights a critical concept for numeric time vectors: the units of the Sen's slope are determined by the units of the time vector `t`.

## Key Concepts
The Mann-Kendall test for significance (p-value, S-statistic, Z-score) is **rank-based**. It only cares about the order of the data, not the numeric difference between timestamps. As a result, the significance of a trend will be the same regardless of the scale of your time vector.

However, the Sen's slope calculation is based on the formula `(y2 - y1) / (t2 - t1)`. This means its magnitude and units depend directly on the units of `t`.

-   If `t = [0, 1, 2, ...]`, the slope is in **units per index step**.
-   If `t = [2010, 2011, ...]` the slope is in **units per year**.

## The Python Script
The script below analyzes the exact same `values` twice, but provides a different numeric time vector `t` for each analysis.

```python

import numpy as np
import MannKenSen as mks

# 1. Generate Data
np.random.seed(42)
years = np.arange(2010, 2020)
noise = np.random.normal(0, 0.5, len(years))
trend = np.linspace(0, 5, len(years))
values = 10 + trend + noise

# 2. Run with integer time vector
print("--- Analysis with t = [0, 1, 2, ...] ---")
t_integer = np.arange(len(years))
result_integer = mks.trend_test(x=values, t=t_integer)
print(f"P-value={result_integer.p:.4f}, S-statistic={result_integer.s}, Slope={result_integer.slope:.4f} (units per index)")

# 3. Run with year time vector
print("\n--- Analysis with t = [2010, 2011, ...] ---")
t_years = years
result_years = mks.trend_test(x=values, t=t_years)
print(f"P-value={result_years.p:.4f}, S-statistic={result_years.s}, Slope={result_years.slope:.4f} (units per year)")

```

## Command Output
Running the script produces the following results:

```
--- Analysis with t = [0, 1, 2, ...] ---
P-value=0.0003, S-statistic=41.0, Slope=0.5480 (units per index)

--- Analysis with t = [2010, 2011, ...] ---
P-value=0.0003, S-statistic=41.0, Slope=0.5480 (units per year)
```

## Interpretation of Results
Notice that the **P-value** and **S-statistic** are identical in both runs. The statistical evidence for the trend's existence is the same.

However, the **Slope** is different.
-   In the first run, the slope is `~0.55`. This is the change in the value for every one-unit increase in the time index.
-   In the second run, the slope is also `~0.55`, but because the time vector is now in years, this value is directly interpretable as **units per year**.

**Conclusion:** Although you can use any monotonically increasing numeric vector for `t`, it is a best practice to use a time vector with meaningful units (e.g., decimal years) whenever possible. This ensures the Sen's slope is directly interpretable without needing further conversion.
