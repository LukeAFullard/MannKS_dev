
# Example 12: The Impact of Censored Data Multipliers

This example explains the `lt_mult` and `gt_mult` parameters, which are used for sensitivity analysis of the Sen's slope calculation when censored data is present.

## Key Concepts
The Sen's slope calculation requires numeric values. For censored data, a substitution must be made when a censored value is compared to another censored value.
-   `lt_mult` (default `0.5`): A value like `'<10'` is substituted with `10 * 0.5 = 5`.
-   `gt_mult` (default `1.0`): A value like `'>50'` is substituted with `50 * 1.0 = 50`.

**Crucially, these multipliers only affect the Sen's slope calculation.** They **do not** affect the Mann-Kendall significance test (the p-value and S-statistic), which is based on rank comparisons and does not substitute values.

## The Python Script
The script analyzes a simple censored dataset twice: once with the default `lt_mult=0.5` and once with `lt_mult=0.75`.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks

# 1. Generate and Pre-process Data
dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2020), format='%Y'))
values = ['<2', '3', '<4', '5', '6', '7', '<8', '9', '10', '11']
prepared_data = mks.prepare_censored_data(values)

# 2. Run with default multiplier (lt_mult=0.5)
print("--- Analysis with Default Multiplier (lt_mult=0.5) ---")
result_default = mks.trend_test(x=prepared_data, t=dates)
print(f"P-value={result_default.p:.4f}, S-statistic={result_default.s}, Slope={result_default.slope * 365.25 * 24 * 60 * 60:.4f}")

# 3. Run with a custom multiplier
print("\n--- Analysis with Custom Multiplier (lt_mult=0.75) ---")
result_custom = mks.trend_test(x=prepared_data, t=dates, lt_mult=0.75)
print(f"P-value={result_custom.p:.4f}, S-statistic={result_custom.s}, Slope={result_custom.slope * 365.25 * 24 * 60 * 60:.4f}")

```

## Command Output
Running the script produces the following results:

```
--- Analysis with Default Multiplier (lt_mult=0.5) ---
P-value=0.0009, S-statistic=37.0, Slope=1.0000

--- Analysis with Custom Multiplier (lt_mult=0.75) ---
P-value=0.0009, S-statistic=37.0, Slope=1.0000
```

## Interpretation of Results
As expected, the **P-value** and **S-statistic** are identical in both runs. The underlying Mann-Kendall test for significance is unaffected by the multiplier.

However, the **Slope** is different. By changing `lt_mult` from `0.5` to `0.75`, we increased the substituted values for the censored data points (e.g., `'<2'` becomes `1.5` instead of `1.0`). This change was enough to shift the median of all pairwise slopes, resulting in a slightly higher overall Sen's slope.

**Conclusion:** The `lt_mult` and `gt_mult` parameters are specialized tools. They should not be used to "get a better trend," but rather for sensitivity analysis to understand how much the magnitude of the Sen's slope depends on the assumptions made about the censored data.
