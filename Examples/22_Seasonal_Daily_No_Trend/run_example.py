
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 22, demonstrating
    a seasonal trend test on daily data with no long-term trend.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Synthetic Data
        np.random.seed(1)
        n_years = 4
        t = pd.to_datetime(pd.date_range(start='2020-01-01', periods=n_years * 365, freq='D'))

        # Create a strong seasonal pattern (sine wave over the year)
        seasonal_cycle = 10 * np.sin(2 * np.pi * t.dayofyear / 365.25)

        # Add noise, but NO long-term trend
        noise = np.random.normal(0, 2.0, len(t))
        x = seasonal_cycle + noise

        # 2. Run the Seasonal Trend Test
        plot_path = 'seasonal_daily_no_trend.png'
        # We test for trends within each month, so period is 12
        result = mks.seasonal_trend_test(x, t, season_type='month', period=12, plot_path=plot_path)

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
# Example 22: Seasonal Trend with Daily Data (No Trend)

A key capability of the seasonal trend test is to distinguish between a true long-term trend and strong, regular seasonality. A dataset can have a very prominent seasonal pattern but no actual year-over-year trend.

This example demonstrates how the test correctly identifies "No Trend" in such a scenario.

## The Python Script

The following script generates 4 years of daily data. The data has a strong sinusoidal pattern, simulating high values in the summer and low values in the winter. Crucially, **no long-term trend** is added.

```python
{code_block}
```

## Command Output

Running the script produces a single result object. The test analyzes the trend *within* each season (e.g., it compares all January data across the years, all February data, etc.) and combines the results.

```
{output_str}
```

## Interpretation of Results

Because there is no year-over-year trend in any month, the combined result correctly shows no overall trend. The high p-value and **'No Trend'** classification confirm that the test was not fooled by the strong seasonal pattern.

## Plot

The plot clearly visualizes the situation. The main plot (top left) shows the strong yearly cycle. However, each of the seasonal subplots (for each month) shows a nearly horizontal trend line, confirming the absence of a long-term trend within any given month.

![Seasonal Daily No Trend Plot](seasonal_daily_no_trend.png)
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plot for Example 22.")

if __name__ == '__main__':
    generate_readme()
