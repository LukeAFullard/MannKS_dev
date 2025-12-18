
# Example 9: Comparing Right-Censored Data Methods (`mk_test_method`)

When a dataset contains right-censored (greater-than) values (e.g., `>10`), the `MannKenSen` package offers two distinct methods for handling them in the Mann-Kendall test, controlled by the `mk_test_method` parameter. This choice can have a significant impact on the results.

This example provides a direct comparison between the two methods.

## 1. Data Generation

We create a small dataset with a weak increasing trend and several right-censored values.

```python
import numpy as np
import MannKenSen

# Generate data with right-censored values
x_censored = ['5.1', '>7.0', '5.3', '6.0', '6.4', '>6.7', '6.2', '6.3', '>7.1', '6.8', '>7.2']
t = np.arange(2010, 2021)

# Prepare the data for analysis
x = MannKenSen.prepare_censored_data(x_censored)
```

## 2. Method Comparison

We run the `trend_test` on the same data twice, changing only the `mk_test_method`.

### Method 1: `mk_test_method='robust'` (Default)

This is the default and statistically recommended method. It handles right-censored data non-parametrically.

-   A right-censored value (e.g., `>7`) is treated as having a rank higher than any observed, non-censored value less than 7.
-   When comparing `>7` to a non-censored value like `8`, the outcome is considered **ambiguous** (it contributes 0 to the S-statistic) because 8 could be less than, equal to, or greater than the true (unknown) value.

```python
result_robust = MannKenSen.trend_test(x, t, mk_test_method='robust')
print(result_robust)
```
**Result (`robust`):** `p=0.1158, z=1.5725, classification='No Trend'`

### Method 2: `mk_test_method='lwp'`

This method replicates a heuristic used in the LWP-TRENDS R script. It is less statistically pure but is provided for backward compatibility.

-   It finds the maximum right-censored detection limit in the dataset (in this case, 7.2).
-   It **replaces all right-censored values** with a number slightly larger than this maximum (e.g., `7.3`).
-   It then treats these substituted values as regular, non-censored numbers. This eliminates the ambiguity described above.

```python
result_lwp = MannKenSen.trend_test(x, t, mk_test_method='lwp')
print(result_lwp)
```
**Result (`lwp`):** `p=0.1021, z=1.6348, classification='No Trend'`

## 3. Conclusion

The **`'robust'`** method, being more statistically conservative, correctly identifies **'No Trend'** in this ambiguous dataset.

The **`'lwp'`** method, by substituting values and removing ambiguity, finds a **'No Trend'**. While this may seem more sensitive, it is based on a heuristic (value substitution) rather than a purely rank-based statistical approach.

For most scientific applications, the default **`'robust'`** method is the recommended choice.
