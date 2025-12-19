
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 6, comparing
    the 'robust' and 'lwp' methods for handling censored data.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
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
        print("\\n--- Analysis with mk_test_method='lwp' ---")
        lwp_plot_file = 'lwp_method_plot.png'
        result_lwp = mks.trend_test(
            x=prepared_data, t=dates, mk_test_method='lwp', plot_path=lwp_plot_file
        )
        print(result_lwp)
    """)

    # --- 2. Execute the Code Block to Get Outputs ---
    f = io.StringIO()
    original_dir = os.getcwd()
    os.chdir(output_dir)
    with redirect_stdout(f):
        exec(code_block, {'np': np, 'pd': pd, 'mks': mks, 'os': os})
    os.chdir(original_dir)
    output_str = f.getvalue().strip()


    # --- 3. Construct the README ---
    readme_content = f"""
# Example 6: Deep Dive into Censored Data Options

This example compares the two methods for handling right-censored data in the Mann-Kendall test: `'robust'` (the default) and `'lwp'`. The choice of method can impact the test's sensitivity, especially when uncensored values are near the censoring limit.

## The Python Script

The script generates data with a key feature: an uncensored value (`12`) that is greater than a right-censored limit (`>10`). This creates an ambiguous comparison. It runs the trend test using both `mk_test_method` options.

```python
{code_block}
```

## Command Output

Running the script produces the following results for each method:

```
{output_str}
```

## Interpretation of Results

### Robust Method (`mk_test_method='robust'`)
This conservative approach treats the comparison between `12` (at a later time) and `>10` (at an earlier time) as ambiguous, contributing 0 to the S-statistic. It cannot be certain if the true value of `>10` is greater or less than 12.

![Robust Method Plot](robust_method_plot.png)

### LWP Method (`mk_test_method='lwp'`)
This method replaces all `>` values with a number slightly larger than the maximum detection limit. In this case, `>10` and `>20` are both replaced with `~20.1`. The comparison between `12` and the substituted `~20.1` is now considered a *decrease*, contributing -1 to the S-statistic. This results in a slightly lower S-score and a different p-value.

![LWP Method Plot](lwp_method_plot.png)

**Conclusion:** The `'robust'` method is generally recommended as it does not invent data. The `'lwp'` method is provided for users who need to replicate results from the LWP-TRENDS R script, which uses this substitution heuristic.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plots for Example 6.")

if __name__ == '__main__':
    generate_readme()
