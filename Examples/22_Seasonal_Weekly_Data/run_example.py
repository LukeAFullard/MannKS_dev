
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 21, demonstrating
    a seasonal trend test on weekly data.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Synthetic Data
        np.random.seed(42)
        n_years = 5
        t = pd.to_datetime(pd.date_range(start='2018-01-01', periods=n_years * 52, freq='W'))

        # Create a long-term decreasing trend
        long_term_trend = np.linspace(10, 0, len(t))

        # Create a weekly seasonal pattern (lower on weekends)
        seasonal_pattern = np.array([-0.5 if day in [5, 6] else 0.5 for day in t.dayofweek])

        # Combine with noise
        noise = np.random.normal(0, 0.5, len(t))
        x = long_term_trend + seasonal_pattern + noise

        # 2. Run the Seasonal Trend Test
        plot_path = 'seasonal_weekly_trend.png'
        # For 'day_of_week', the period is 7
        result = mks.seasonal_trend_test(x, t, season_type='day_of_week', period=7, plot_path=plot_path)

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
# Example 21: Seasonal Trend with Weekly Data

The `MannKenSen` package is not limited to monthly or annual seasons. It can perform seasonal trend analysis on any regular time interval by specifying the `season_type` and `period`.

This example demonstrates an analysis of weekly data, testing for an overall trend while accounting for variations between each day of the week.

## The Python Script

The following script generates 5 years of weekly data with two patterns:
1.  A steady long-term **decreasing** trend.
2.  A weekly seasonal pattern where values are slightly lower on weekends (Saturday and Sunday).

```python
{code_block}
```

## Command Output

Running the script produces a single result object that summarizes the overall trend across all seasons (days of the week).

```
{output_str}
```

## Interpretation of Results

The result shows a **'Highly Likely Decreasing'** trend with a very small p-value. The test combines the evidence from each day of the week to produce one set of statistics. It successfully identified the strong, underlying decreasing trend present in the data, even with the weekly seasonal pattern.

## Plot

The generated plot is the primary tool for visualizing the behavior of individual seasons. Each subplot shows the data for a specific day of the week (Monday=0, Sunday=6). The plot visually confirms that a decreasing trend is present for every day, consistent with the overall result.

![Seasonal Weekly Trend Plot](seasonal_weekly_trend.png)
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plot for Example 21.")

if __name__ == '__main__':
    generate_readme()
