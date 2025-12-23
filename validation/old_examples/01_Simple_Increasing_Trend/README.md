# Validation Case V-01: Simple Increasing Trend

## Objective
This validation case verifies that all methods can correctly identify a statistically significant, positive trend in a simple, non-seasonal, uncensored dataset.

## Data
A synthetic dataset of 50 annual samples was generated with a known positive slope.

```python
import pandas as pd
import numpy as np
import MannKenSen as mk

# Generate Data
np.random.seed(42)
n = 50
t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='YE'))
slope = 0.1
intercept = 5
noise = np.random.normal(0, 1, n)
x = slope * np.arange(n) + intercept + noise

# Run MannKenSen (Standard)
mk_standard = mk.trend_test(x, t)

# Run MannKenSen (LWP Mode)
mk_lwp = mk.trend_test(
    x, t,
    mk_test_method='lwp',
    ci_method='lwp',
    tie_break_method='lwp'
)

print("Standard MK p-value:", mk_standard.p)
print("LWP MK p-value:", mk_lwp.p)
```

## Results Comparison

The following table compares the key statistical outputs from the three analysis methods.

| Metric              | MannKenSen (Standard) | MannKenSen (LWP Mode) | LWP-TRENDS R Script |
|---------------------|-----------------------|-----------------------|---------------------|
| p-value             | 0.000000   | 0.000000        | 0.000000     |
| Sen's Slope         | 0.087639 | 0.087639    | 0.087639       |
| Lower CI (90%)      | 0.070587 | 0.070635 | 0.070635    |
| Upper CI (90%)      | 0.103204 | 0.103189 | 0.103189    |

## Analysis

The results show that all three methods correctly identified a significant increasing trend (p < 0.05).

As expected, the results from **MannKenSen (LWP Mode)** are nearly identical to the **LWP-TRENDS R Script**. This confirms that the LWP-compatibility settings in `mannkensen` are working correctly for a basic, non-seasonal, uncensored case. The minor differences can be attributed to floating-point precision differences between Python and R.

The **MannKenSen (Standard)** results are also very similar, which is expected for a simple dataset with no ties or censoring, where the different statistical methods should converge.