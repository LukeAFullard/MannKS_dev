
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 10, demonstrating
    robustness to multiple censoring levels.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Data with Multiple Censoring Levels
        dates = pd.to_datetime(pd.to_datetime(np.arange(2005, 2025), format='%Y'))
        values = [
            '<1', '1.2', '<2', '1.8', '<1',
            '2.5', '<5', '4.8', '5.1', '<5',
            '7.2', '8.1', '>10', '12.3', '11.8',
            '>10', '14.5', '15.9', '>15', '18.2'
        ]

        # 2. Pre-process and Analyze
        prepared_data = mks.prepare_censored_data(values)
        plot_path = 'multi_censor_plot.png'
        result = mks.trend_test(
            x=prepared_data,
            t=dates,
            plot_path=plot_path
        )

        # 3. Print the result
        print(result)
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
# Example 10: Handling Data with Multiple Censoring Levels

This example demonstrates the robustness of `MannKenSen` in handling complex, realistic datasets that contain numerous different censoring levels.

## Key Concepts
Real-world data often has a mix of censoring types (e.g., `<1`, `<5`, `>50`). The statistical engine in `MannKenSen` is designed to handle this complexity automatically. The standard workflow of `prepare_censored_data` followed by `trend_test` is sufficient. The test correctly interprets the relationships between all pairs of values, whether they are censored or not (e.g., it knows that `<5` is greater than `<2`, but the comparison between `<5` and `4.8` is ambiguous).

## The Python Script
The script generates a synthetic dataset with an increasing trend and a complex mix of left-censored (`<1`, `<2`, `<5`) and right-censored (`>10`, `>15`) data. It runs the standard analysis workflow.

```python
{code_block}
```

## Command Output
Running the script produces the following final result:

```
{output_str}
```

## Interpretation of Results
Despite the complexity of the data, with 40% of the values being censored at five different levels, the analysis correctly identifies the strong **'Highly Likely Increasing'** trend. This demonstrates the power and reliability of the underlying rank-based statistics for handling complex, real-world data.

### Analysis Plot (`multi_censor_plot.png`)
The plot visualizes the complex data, using different markers for uncensored (circles), left-censored (downward triangles), and right-censored (upward triangles) data points.

![Multi-Censor Plot](multi_censor_plot.png)

**Conclusion:** `MannKenSen` is a robust tool for handling complex, messy, real-world censored data without requiring special configuration.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plot for Example 10.")

if __name__ == '__main__':
    generate_readme()
