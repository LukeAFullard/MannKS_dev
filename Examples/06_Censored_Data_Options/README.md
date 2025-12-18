
# Example 6: Deep Dive into Censored Data Options

This example compares the two methods for handling right-censored data in the Mann-Kendall test: `'robust'` (the default) and `'lwp'`. The choice of method can impact the test's sensitivity, especially when uncensored values are near the censoring limit.

## Key Concepts

-   **`mk_test_method='robust'` (Default):** This conservative approach treats a comparison between an uncensored value and a right-censored value as ambiguous (contributing 0 to the S-statistic) if the uncensored value is greater than the detection limit (e.g., `12` vs. `>10`).
-   **`mk_test_method='lwp'`:** This method emulates the LWP-TRENDS R script. It replaces all right-censored values with a number slightly higher than the maximum uncensored value, making the test less conservative. For example, the comparison `12` vs. `>10` is now treated as a decrease (-1 to S-statistic).

## Script: `run_example.py`
The script generates data with a key feature: an uncensored value (`12`) that is greater than a right-censored limit (`>10`). It runs the trend test using both methods and generates this README.

## Results

### Robust Method (`mk_test_method='robust'`)

- **Classification:** Highly Likely Increasing
- **P-value:** 0.0030
- **S-statistic:** 42.0
- **Sen's Slope:** 1.2251

![Robust Method Plot](robust_method_plot.png)

### LWP Method (`mk_test_method='lwp'`)

- **Classification:** Highly Likely Increasing
- **P-value:** 0.0026
- **S-statistic:** 45.0
- **Sen's Slope:** 1.2251

![LWP Method Plot](lwp_method_plot.png)

### Interpretation
The `'robust'` method produces a lower S-statistic because it treats the ambiguous `12` vs. `>10` comparison as a tie. The `'lwp'` method treats this as a decrease, resulting in a different S-statistic and p-value.

**Conclusion:** The `'robust'` method is generally recommended. The `'lwp'` method is for users who need to replicate results from the LWP-TRENDS R script.
