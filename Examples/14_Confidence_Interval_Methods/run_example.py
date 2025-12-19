
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 13, comparing
    the confidence interval calculation methods.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Data
        np.random.seed(42)
        dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2025), format='%Y'))
        noise = np.random.normal(0, 2, len(dates))
        trend = np.linspace(0, 10, len(dates))
        values = 5 + trend + noise

        # 2. Run with 'direct' method (Default)
        print("--- Analysis with ci_method='direct' ---")
        direct_plot_file = 'direct_ci_plot.png'
        result_direct = mks.trend_test(
            x=values, t=dates, ci_method='direct', plot_path=direct_plot_file
        )
        s_in_y = 365.25 * 24 * 60 * 60
        print(f"Annual Slope: {result_direct.slope * s_in_y:.4f}")
        print(f"Annual CI: ({result_direct.lower_ci * s_in_y:.4f}, {result_direct.upper_ci * s_in_y:.4f})")


        # 3. Run with 'lwp' method
        print("\\n--- Analysis with ci_method='lwp' ---")
        lwp_plot_file = 'lwp_ci_plot.png'
        result_lwp = mks.trend_test(
            x=values, t=dates, ci_method='lwp', plot_path=lwp_plot_file
        )
        print(f"Annual Slope: {result_lwp.slope * s_in_y:.4f}")
        print(f"Annual CI: ({result_lwp.lower_ci * s_in_y:.4f}, {result_lwp.upper_ci * s_in_y:.4f})")
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
# Example 13: Comparing Confidence Interval Methods

This example compares the two methods for calculating the confidence intervals (CI) for the Sen's slope: `'direct'` (default) and `'lwp'`.

## Key Concepts
-   `'direct'` **(Default):** This method calculates the ranks of the upper and lower CIs and rounds them to the nearest integer. It then uses these integers to directly index the sorted array of pairwise slopes.
-   `'lwp'`: This method emulates the LWP-TRENDS R script by using linear interpolation between the ranks of the sorted slopes to find a more precise, interpolated CI value.

The choice of method does **not** affect the Sen's slope itself, only the upper and lower bounds of its confidence interval.

## The Python Script
The script analyzes a simple linear dataset twice, once with each `ci_method`.

```python
{code_block}
```

## Command Output
Running the script produces the following results:

```
{output_str}
```

## Interpretation of Results
As expected, the **Annual Slope** is identical in both runs. However, the **Annual CI** is slightly different. The `'lwp'` method, using interpolation, produces slightly different bounds than the direct indexing `'direct'` method. The difference is usually small but can be meaningful in certain analyses.

### Direct CI Method (`ci_method='direct'`)
![Direct CI Plot](direct_ci_plot.png)

### LWP CI Method (`ci_method='lwp'`)
![LWP CI Plot](lwp_ci_plot.png)

**Conclusion:** The default `'direct'` method is generally sufficient and computationally simpler. The `'lwp'` method is provided for users who need consistency with the LWP-TRENDS R script or who have a specific analytical need for an interpolated confidence interval.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plots for Example 13.")

if __name__ == '__main__':
    generate_readme()
