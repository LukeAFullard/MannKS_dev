
# Example 20: Sen's Slope Methods for Censored Data (`sens_slope_method`)

When calculating the Sen's slope, the slope between certain pairs of censored data points is statistically ambiguous. For example, the true slope between two left-censored values (`<5` and `<8`) is unknown. The `sens_slope_method` parameter controls how these ambiguous slopes are handled.

## The Python Script

The script below creates a dataset with an ambiguous pair of left-censored values. It analyzes the data twice: once with the default `sens_slope_method='nan'` and once with `sens_slope_method='lwp'`.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks

# 1. Generate Data with Ambiguous Slopes
# The slope between two left-censored values ('<5' and '<8') is ambiguous.
t = np.arange(2015, 2021)
x_censored = ['<5', '6', '7', '<8', '9', '10']
x = mks.prepare_censored_data(x_censored)

# 2. Run with 'nan' method (Default)
print("--- Analysis with sens_slope_method='nan' ---")
result_nan = mks.trend_test(x, t, sens_slope_method='nan')
print(f"Slope: {result_nan.slope:.4f}, P-value: {result_nan.p:.4f}")

# 3. Run with 'lwp' method
print("\n--- Analysis with sens_slope_method='lwp' ---")
result_lwp = mks.trend_test(x, t, sens_slope_method='lwp')
print(f"Slope: {result_lwp.slope:.4f}, P-value: {result_lwp.p:.4f}")

```

## Command Output

Running the script produces the following results:

```
--- Analysis with sens_slope_method='nan' ---
Slope: 1.0000, P-value: 0.0289

--- Analysis with sens_slope_method='lwp' ---
Slope: 0.0000, P-value: 0.0289
```

## Interpretation of Results

**Crucially, notice that the P-value is identical in both runs.** This parameter only affects the calculation of the Sen's slope magnitude; it does not change the significance of the trend from the Mann-Kendall test.

### Method 1: `sens_slope_method='nan'` (Default)

**Justification:** This is the default and most statistically sound method.

**How it works:** When a pairwise slope is ambiguous (e.g., between `<5` and `<8`), it is set to `np.nan` and is **excluded** from the median calculation. This means the final Sen's slope is the median of only the unambiguous slopes. In our example, the slope is **1.0000**.

### Method 2: `sens_slope_method='lwp'`

**Justification:** This method replicates a heuristic from the LWP-TRENDS R script and is provided for backward compatibility.

**How it works:** When a pairwise slope is ambiguous, it is set to **`0`**. This value is then included in the median calculation. By including these zero-slopes, this method biases the final Sen's slope towards zero. In our example, this pushes the slope down to **0.0000**.

### Conclusion

| Method   | Ambiguous Slope Value | Recommendation                               |
|----------|-----------------------|----------------------------------------------|
| **`nan`**    | `np.nan` (Excluded)   | **Recommended for most scientific applications.** |
| **`lwp`**    | `0` (Included)        | Use only for backward compatibility.         |

For rigorous analysis, the default **`'nan'`** method is the superior choice because it does not introduce an artificial bias towards zero in the slope calculation.
