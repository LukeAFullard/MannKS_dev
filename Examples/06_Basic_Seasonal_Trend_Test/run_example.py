
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 5, demonstrating
    the basic seasonal trend test workflow.
    """
    # --- 1. Define Paths and Code Block ---
    output_dir = os.path.dirname(__file__)

    code_block = textwrap.dedent("""
        import numpy as np
        import pandas as pd
        import MannKenSen as mks
        import os

        # 1. Generate Synthetic Seasonal Data
        np.random.seed(42)
        dates = pd.date_range(start='2010-01-01', end='2019-12-31', freq='ME')
        n = len(dates)

        # Create a strong seasonal cycle (high in winter, low in summer)
        seasonal_pattern = 10 * np.cos(2 * np.pi * (dates.month - 1) / 12) + 20
        # Create a slight, underlying increasing trend
        trend = np.linspace(0, 5, n)
        # Combine with noise
        values = seasonal_pattern + np.random.normal(0, 2, n) + trend

        # --- The 3-Step Seasonal Analysis Workflow ---
        dist_plot_file = 'seasonal_distribution_plot.png'
        trend_plot_file = 'seasonal_trend_plot.png'

        # 2. Step 1: Statistically Check for Seasonality
        print("--- 1. Seasonality Check ---")
        seasonality_result = mks.check_seasonality(x_old=values, t_old=dates, season_type='month')
        print(f"Is Seasonal?: {seasonality_result.is_seasonal} (p={seasonality_result.p_value:.2e})")

        # 3. Step 2: Visualize Seasonal Distribution
        print("\\n--- 2. Visualizing Seasonality ---")
        print(f"Generating seasonal distribution plot: {dist_plot_file}")
        mks.plot_seasonal_distribution(
            x_old=values, t_old=dates, season_type='month', save_path=dist_plot_file
        )

        # 4. Step 3: Perform Seasonal Trend Test
        print("\\n--- 3. Seasonal Trend Test ---")
        seasonal_trend_result = mks.seasonal_trend_test(
            x=values, t=dates, season_type='month', plot_path=trend_plot_file
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
# Example 5: Basic Seasonal Trend Test

This example demonstrates the standard workflow for analyzing time series data that has a seasonal pattern. Strong seasonality can mask or create spurious long-term trends, so it's essential to use a seasonal test to correctly identify the underlying trend.

The workflow involves three key steps:
1.  **Check for Seasonality:** Statistically determine if a seasonal pattern exists.
2.  **Visualize Seasonality:** Use a box plot to visually confirm the pattern.
3.  **Perform Seasonal Test:** If seasonality is present, use the `seasonal_trend_test` to find the long-term trend.

## The Python Script

The script generates 10 years of synthetic monthly data containing a strong seasonal cycle (high in winter, low in summer) and a slight, underlying increasing trend. It then performs the three steps outlined above.

```python
{code_block}
```

## Command Output

Running the script produces the following output, showing the results from each step of the workflow.

```
{output_str}
```

## Interpretation of Results

### 1. Seasonality Check
The `check_seasonality` function uses the Kruskal-Wallis H-test. The very low p-value (`p < 0.01`) confirms that the data is statistically seasonal.

### 2. Seasonal Distribution Plot
This box plot visualizes the data distribution for each month, clearly showing the cosine pattern that was generated in the synthetic data. This visual check confirms the statistical result.

![Seasonal Distribution Plot](seasonal_distribution_plot.png)

### 3. Seasonal Trend Test
Since seasonality was confirmed, we use `seasonal_trend_test`. This function analyzes the trend for each season (month) individually before combining them. This correctly isolates the long-term trend from the seasonal cycle, identifying the underlying **'Highly Likely Increasing'** trend.

The final trend plot shows the raw data points with the calculated seasonal Sen's slope and its confidence intervals overlaid, confirming the slight increasing trend.

![Seasonal Trend Plot](seasonal_trend_plot.png)

**Conclusion:** This workflow—confirm, visualize, and then test for seasonal trend—is a robust method for analyzing seasonal time series data and correctly identifying long-term trends.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plots for Example 5.")

if __name__ == '__main__':
    generate_readme()
