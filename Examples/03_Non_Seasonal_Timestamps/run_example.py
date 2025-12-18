
import os
import numpy as np
import pandas as pd
import MannKenSen as mks
import textwrap
import io
from contextlib import redirect_stdout

def generate_readme():
    """
    Generates a comprehensive README.md file for Example 3, demonstrating
    a trend test with datetime objects.
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
        n_samples = 120 # 10 years of monthly data
        dates = pd.date_range(start='2010-01-01', periods=n_samples, freq='MS')

        # Create a slight downward trend of ~0.5 units per year
        time_as_years = np.arange(n_samples) / 12.0
        trend = -0.5 * time_as_years
        noise = np.random.normal(0, 0.8, n_samples)
        values = 10 + trend + noise

        # 2. Perform the Trend Test with Plotting
        plot_path = 'timestamp_trend_plot.png'
        result = mks.trend_test(x=values, t=dates, plot_path=plot_path)

        # 3. Print the full result
        print(result)

        # 4. Convert slope to annual units for interpretation
        SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60
        annual_slope = result.slope * SECONDS_PER_YEAR
        print(f"\\nAnnual Sen's Slope: {annual_slope:.4f} (units per year)")
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
# Example 3: Non-Seasonal Trend Test with Timestamps

This example demonstrates how to perform a trend test on a time series that uses `datetime` objects for its time vector, a common format for real-world data. It also shows how to generate a trend plot and interpret the slope when using timestamps.

## The Python Script

The script generates 10 years of synthetic monthly data with a slight downward trend. It then calls `mks.trend_test`, passing the `pandas.DatetimeIndex` as the time vector `t`, and uses the `plot_path` argument to save a visualization.

```python
{code_block}
```

## Command Output

Running the script prints the full result object, followed by the calculated annual slope.

```
{output_str}
```

## Interpretation of Results

*   **Slope Calculation:** When `datetime` objects are used, the raw `slope` is calculated in **units per second**. To make it interpretable, you must convert it to a more useful time unit, such as years. The script shows how to do this, resulting in an **Annual Sen's Slope** that is consistent with the -0.5 units/year we built into the data.
*   **Significance:** The very low p-value and **'Highly Likely Decreasing'** classification confirm that a statistically significant downward trend was detected.

### Plot Interpretation (`timestamp_trend_plot.png`)
The generated plot provides a comprehensive visual summary:
-   **Data Points:** The raw monthly data points are plotted over time.
-   **Sen's Slope Line:** The solid red line shows the calculated Sen's slope, clearly visualizing the downward trend.
-   **Confidence Intervals:** The dashed red lines show the 95% confidence intervals for the slope.

![Trend Plot](timestamp_trend_plot.png)

**Conclusion:** The `MannKenSen` package seamlessly handles `datetime` objects. Remember to convert the slope to your desired time unit for a meaningful interpretation.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plot for Example 3.")

if __name__ == '__main__':
    generate_readme()
