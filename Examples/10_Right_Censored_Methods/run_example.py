
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md for Example 9, clarifying the
    methodological differences between 'robust' and 'lwp' for right-censored data.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks

        # 1. Generate Data with Right-Censored Values
        x_censored = ['5.1', '>7.0', '5.3', '6.0', '6.4', '>6.7', '6.2', '6.3', '>7.1', '6.8', '>7.2']
        t = np.arange(2010, 2021)

        # 2. Prepare the data for analysis
        x = mks.prepare_censored_data(x_censored)

        # 3. Run analysis with the 'robust' method (Default)
        print("--- Analysis with mk_test_method='robust' ---")
        result_robust = mks.trend_test(x, t, mk_test_method='robust', alpha=0.1)
        print(result_robust)

        # 4. Run analysis with the 'lwp' method
        print("\\n--- Analysis with mk_test_method='lwp' ---")
        result_lwp = mks.trend_test(x, t, mk_test_method='lwp', alpha=0.1)
        print(result_lwp)
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    exec_globals = {'np': np, 'pd': pd, 'mks': mks}
    with redirect_stdout(f):
        exec(code_block, exec_globals)
    output_str = f.getvalue().strip()

    result_robust = exec_globals['result_robust']
    result_lwp = exec_globals['result_lwp']

    # --- 3. Construct the README ---
    readme_content = f"""
# Example 9: Comparing Right-Censored Data Methods (`mk_test_method`)

When a dataset contains right-censored (greater-than) values like `>10`, the true value is unknown. The `MannKenSen` package provides two distinct methods for handling this uncertainty in the Mann-Kendall test, controlled by the `mk_test_method` parameter.

This example provides a direct comparison of these two methods, with clear justifications for their behavior.

## The Python Script

The following script creates a dataset with a weak increasing trend and several right-censored values. It then runs the trend test twice: once with the default `'robust'` method, and once with the `'lwp'` method. A lenient `alpha=0.1` is used to better highlight the difference.

```python
{code_block}
```

## Command Output

Running the script produces the following results for each method:

```
{output_str}
```

## Interpretation of Results

### Method 1: `mk_test_method='robust'` (Default)

**Justification:** This is the default and most statistically sound method. It is a non-parametric approach that relies only on rank information and does not invent or substitute data.

**How it works:**
-   A right-censored value (e.g., `>7.0`) is treated as having a rank higher than any observed, non-censored value below 7.0.
-   When comparing `>7.0` to a non-censored value like `8.0`, the result is **ambiguous**. We cannot know if the true value of `>7.0` is less than, equal to, or greater than 8.0. In these cases, the `'robust'` method assigns a score of 0 to the comparison, making no assumption.

In our dataset, this ambiguity reduces the overall evidence for a trend, leading to a higher p-value (`{result_robust.p:.4f}`) and a **`{result_robust.classification}`** classification.

### Method 2: `mk_test_method='lwp'`

**Justification:** This method replicates a heuristic from the LWP-TRENDS R script. It is provided for users who need to reproduce results from that specific software. It is not recommended for general scientific use because it involves data substitution.

**How it works:**
-   First, it scans the entire dataset to find the highest right-censored detection limit (in this case, `7.2` from `>7.2`).
-   It then **replaces all right-censored values** with a single, arbitrary number that is slightly larger than this maximum (e.g., `7.3`).
-   Finally, it treats these substituted values as if they were true, non-censored measurements.

This process eliminates all ambiguity, but it does so by inventing data. In our example, this substitution strengthens the apparent trend, leading to a lower p-value (`{result_lwp.p:.4f}`) and a **`{result_lwp.classification}`** classification.

### Conclusion

| Method   | Statistical Approach | Recommendation                               |
|----------|----------------------|----------------------------------------------|
| **`robust`** | Purely rank-based    | **Recommended for most scientific applications.** |
| **`lwp`**    | Data substitution    | Use only for backward compatibility.         |

For rigorous scientific analysis, the default **`'robust'`** method is the superior choice because it does not make arbitrary assumptions about the true values of the censored data.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print(f"Successfully generated README for Example 9.")

if __name__ == '__main__':
    generate_readme()
