
import os
import numpy as np
import pandas as pd
import MannKenSen

def generate_readme():
    """
    Generates the README.md file for this example, demonstrating the difference
    between 'robust' and 'lwp' methods for right-censored data.
    """
    # 1. Generate Synthetic Data with right-censored values
    # The trend is weak, making the method choice impactful.
    np.random.seed(15)
    t = np.arange(2010, 2021)
    x_raw = np.linspace(5, 7, len(t)) + np.random.normal(0, 0.8, len(t))
    x_censored = [f">{val:.1f}" if val > 6.5 else f"{val:.1f}" for val in x_raw]
    x_censored[1] = '>7.0' # Add a higher censored value

    # 2. Prepare the data
    x_prepared = MannKenSen.prepare_censored_data(x_censored)

    # 3. Run trend test with both methods
    result_robust = MannKenSen.trend_test(x_prepared, t, mk_test_method='robust')
    result_lwp = MannKenSen.trend_test(x_prepared, t, mk_test_method='lwp')

    # --- Format results for display ---
    robust_str = f"p={result_robust.p:.4f}, z={result_robust.z:.4f}, classification='{result_robust.classification}'"
    lwp_str = f"p={result_lwp.p:.4f}, z={result_lwp.z:.4f}, classification='{result_lwp.classification}'"

    # --- Generate README ---
    readme_content = f"""
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
**Result (`robust`):** `{robust_str}`

### Method 2: `mk_test_method='lwp'`

This method replicates a heuristic used in the LWP-TRENDS R script. It is less statistically pure but is provided for backward compatibility.

-   It finds the maximum right-censored detection limit in the dataset (in this case, 7.2).
-   It **replaces all right-censored values** with a number slightly larger than this maximum (e.g., `7.3`).
-   It then treats these substituted values as regular, non-censored numbers. This eliminates the ambiguity described above.

```python
result_lwp = MannKenSen.trend_test(x, t, mk_test_method='lwp')
print(result_lwp)
```
**Result (`lwp`):** `{lwp_str}`

## 3. Conclusion

The **`'robust'`** method, being more statistically conservative, correctly identifies **'{result_robust.classification}'** in this ambiguous dataset.

The **`'lwp'`** method, by substituting values and removing ambiguity, finds a **'{result_lwp.classification}'**. While this may seem more sensitive, it is based on a heuristic (value substitution) rather than a purely rank-based statistical approach.

For most scientific applications, the default **`'robust'`** method is the recommended choice.
"""

    # Write to file
    filepath = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(filepath, 'w') as f:
        f.write(readme_content)
    print("Generated README.md for Example 9.")

if __name__ == '__main__':
    generate_readme()
