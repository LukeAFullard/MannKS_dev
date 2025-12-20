
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 11, demonstrating
    advanced seasonality with non-monthly data.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Data with a Weekly Cycle
        np.random.seed(42)
        dates = pd.date_range(start='2018-01-01', end='2020-12-31', freq='D')
        n = len(dates)

        # Create a strong weekly cycle (higher values on weekends)
        seasonal_pattern = np.where(dates.dayofweek.isin([5, 6]), 25, 10)
        # Create an underlying increasing trend
        trend = np.linspace(0, 15, n)
        # Combine with noise
        values = seasonal_pattern + np.random.normal(0, 3, n) + trend

        # 2. Visualize the Seasonal Distribution
        dist_plot_file = 'seasonal_distribution_plot.png'
        mks.plot_seasonal_distribution(
            x=values, t=dates, season_type='day_of_week', period=7, plot_path=dist_plot_file
        )

        # 3. Perform the Seasonal Trend Test
        print("--- Seasonal Trend Test Result ---")
        trend_plot_file = 'seasonal_trend_plot.png'
        seasonal_trend_result = mks.seasonal_trend_test(
            x=values, t=dates, season_type='day_of_week', period=7, plot_path=trend_plot_file
        )
        print(seasonal_trend_result)
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
# Example 11: Advanced Seasonality (Non-Monthly Data)

This example demonstrates the flexibility of `MannKenSen`'s seasonal analysis for non-monthly data, such as a weekly (`day_of_week`) pattern.

## Key Concepts
Seasonal analysis is not limited to monthly data. The `season_type` parameter in `seasonal_trend_test` and `plot_seasonal_distribution` allows analysis of any sub-annual pattern (e.g., weekly, quarterly) by correctly grouping the data. For `day_of_week`, the `period` must be set to `7`.

## The Python Script
The script generates a 3-year daily dataset with a strong weekly cycle (higher values on weekends) and an underlying increasing trend. It then visualizes the weekly pattern and performs a seasonal trend test using `season_type='day_of_week'`.

```python
{code_block}
```

## Command Output
Running the script produces the following result:

```
{output_str}
```

## Interpretation of Results
The test successfully isolates the long-term increasing trend from the strong weekly cycle, resulting in a **'Highly Likely Increasing'** classification.

### Seasonal Distribution Plot
This plot clearly shows the weekly cycle, with higher values for day 5 (Saturday) and 6 (Sunday), confirming the seasonal pattern in the data.

![Seasonal Distribution Plot](seasonal_distribution_plot.png)

### Seasonal Trend Plot
The trend plot shows the overall time series and correctly identifies the underlying increasing trend, separate from the weekly noise.

![Seasonal Trend Plot](seasonal_trend_plot.png)

**Conclusion:** The `season_type` parameter makes `seasonal_trend_test` a versatile tool for analyzing time series data with various cyclical patterns.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plots for Example 11.")

if __name__ == '__main__':
    generate_readme()
