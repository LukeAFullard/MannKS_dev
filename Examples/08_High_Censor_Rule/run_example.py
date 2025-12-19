
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 7, explaining
    the 'hicensor' rule.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Data with Improving Detection Limits
        # The recorded values appear to decrease, but only because the lab's
        # detection limit is getting better over time.
        dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2022), format='%Y'))
        values = ['<10', '<10', '<10', '<5', '<5', '<5', '<2', '<2', '<2', '<1', '<1', '<1']
        prepared_data = mks.prepare_censored_data(values)

        # 2. Run Analysis Without the `hicensor` Rule
        print("--- Analysis Without hicensor Rule ---")
        original_plot_file = 'original_data_plot.png'
        result_original = mks.trend_test(
            x=prepared_data, t=dates, plot_path=original_plot_file
        )
        print(result_original)

        # 3. Run Analysis With the `hicensor` Rule
        print("\\n--- Analysis With hicensor=True ---")
        hicensor_plot_file = 'hicensor_rule_plot.png'
        result_hicensor = mks.trend_test(
            x=prepared_data, t=dates, hicensor=True, plot_path=hicensor_plot_file
        )
        print(result_hicensor)
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
# Example 7: The High Censor Rule (`hicensor`)

Long-term monitoring data often has a "paper trend" caused by improvements in laboratory detection limits over time. For example, if a contaminant was always present but the detection limit improved from `<10` to `<1`, the recorded data might look like a decreasing trend. The `hicensor` rule is a powerful tool to correct for this.

## Key Concept

When `hicensor=True`, the `trend_test` function finds the **highest left-censored detection limit** in the entire dataset (e.g., `10` from `<10`). It then treats all values in the dataset—both censored and uncensored—that are below this limit as if they were censored at that highest limit. For example, `<5`, `<2`, `<1`, and an uncensored value of `8` would all be treated as `<10` for the analysis.

## The Python Script

The script below generates a dataset where the recorded values appear to decrease over time solely because the detection limit is improving. It analyzes the data twice: once without the `hicensor` rule and once with it.

```python
{code_block}
```

## Command Output

Running the script produces the following results:

```
{output_str}
```

## Interpretation of Results

### Analysis Without `hicensor` Rule
Even without the `hicensor` rule, the default robust statistics correctly identify **'No Trend'**. This is because comparisons between different censored levels (e.g., `<10` vs. `<5`) are treated as ambiguous ties, contributing 0 to the trend score. However, the plot still visually suggests a downward trend, which could be misleading.

![Original Data Plot](original_data_plot.png)

### Analysis With `hicensor=True`
Applying the `hicensor` rule makes the analysis more rigorous. All values are treated as `<10`, resulting in a dataset with zero variance. The test correctly and definitively concludes there is **'No Trend'** and produces a plot where all data points are standardized to the highest detection limit, removing the misleading visual "paper trend".

![Hicensor Rule Plot](hicensor_rule_plot.png)

**Conclusion:** While the default statistical methods are robust to paper trends, using the `hicensor` rule provides a more conservative and explicit way to validate your analysis and is highly recommended for any long-term dataset where analytical methods may have changed over time.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plots for Example 7.")

if __name__ == '__main__':
    generate_readme()
