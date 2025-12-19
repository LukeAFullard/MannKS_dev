
# Example 6: Deep Dive into Censored Data Options

This example compares the two methods for handling right-censored data in the Mann-Kendall test: `'robust'` (the default) and `'lwp'`. The choice of method can impact the test's sensitivity, especially when uncensored values are near the censoring limit.

## The Python Script

The script generates data with a key feature: an uncensored value (`12`) that is greater than a right-censored limit (`>10`). This creates an ambiguous comparison. It runs the trend test using both `mk_test_method` options.

```python

import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# 1. Generate Synthetic Data
# This data includes an uncensored value (12) that is greater
# than a right-censored limit (>10), creating ambiguity.
dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2022), format='%Y'))
values = ['5', '6', '7', '>10', '8', '9', '12', '>10', '14', '15', '18', '>20']
prepared_data = mks.prepare_censored_data(values)

# 2. Run with 'robust' method
print("--- Analysis with mk_test_method='robust' ---")
robust_plot_file = 'robust_method_plot.png'
result_robust = mks.trend_test(
    x=prepared_data, t=dates, mk_test_method='robust', plot_path=robust_plot_file
)
print(result_robust)

# 3. Run with 'lwp' method
print("\n--- Analysis with mk_test_method='lwp' ---")
lwp_plot_file = 'lwp_method_plot.png'
result_lwp = mks.trend_test(
    x=prepared_data, t=dates, mk_test_method='lwp', plot_path=lwp_plot_file
)
print(result_lwp)

```

## Command Output

Running the script produces the following results for each method:

```
--- Analysis with mk_test_method='robust' ---
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(0.002985295768966667), z=np.float64(2.969247979949396), Tau=np.float64(0.7793830999764657), s=np.float64(42.0), var_s=np.float64(190.66666666666666), slope=np.float64(3.882051064621181e-08), intercept=np.float64(-45.73997989343973), lower_ci=np.float64(3.16808596918086e-08), upper_ci=np.float64(5.704636728733114e-08), C=0.9985073521155167, Cd=0.0014926478844833335, classification='Highly Likely Increasing', analysis_notes=['WARNING: Sen slope influenced by right-censored values.'], sen_probability=np.float64(1.332221621586826e-05), sen_probability_max=np.float64(0.9999930438565151), sen_probability_min=np.float64(1.332221621586826e-05), prop_censored=np.float64(0.25), prop_unique=0.9166666666666666, n_censor_levels=2)

--- Analysis with mk_test_method='lwp' ---
Mann_Kendall_Test(trend='increasing', h=np.True_, p=np.float64(0.0025512806164449398), z=np.float64(3.017192117824463), Tau=np.float64(0.6978631577988531), s=np.float64(45.0), var_s=np.float64(212.66666666666666), slope=np.float64(3.882051064621181e-08), intercept=np.float64(-45.73997989343973), lower_ci=np.float64(3.16808596918086e-08), upper_ci=np.float64(5.704636728733114e-08), C=0.9987243596917775, Cd=0.0012756403082224699, classification='Highly Likely Increasing', analysis_notes=['WARNING: Sen slope influenced by right-censored values.'], sen_probability=np.float64(3.486461456843177e-05), sen_probability_max=np.float64(0.9999805866460582), sen_probability_min=np.float64(3.486461456843177e-05), prop_censored=np.float64(0.25), prop_unique=0.9166666666666666, n_censor_levels=2)
```

## Interpretation of Results

### Robust Method (`mk_test_method='robust'`)
This conservative approach treats the comparison between `12` (at a later time) and `>10` (at an earlier time) as ambiguous, contributing 0 to the S-statistic. It cannot be certain if the true value of `>10` is greater or less than 12.

![Robust Method Plot](robust_method_plot.png)

### LWP Method (`mk_test_method='lwp'`)
This method replaces all `>` values with a number slightly larger than the maximum detection limit. In this case, `>10` and `>20` are both replaced with `~20.1`. The comparison between `12` and the substituted `~20.1` is now considered a *decrease*, contributing -1 to the S-statistic. This results in a slightly lower S-score and a different p-value.

![LWP Method Plot](lwp_method_plot.png)

**Conclusion:** The `'robust'` method is generally recommended as it does not invent data. The `'lwp'` method is provided for users who need to replicate results from the LWP-TRENDS R script, which uses this substitution heuristic.
