
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
    a trend test with datetime objects and the new slope scaling feature.
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

        # 2. Perform the Trend Test with Plotting and Slope Scaling
        plot_path = 'timestamp_trend_plot.png'
        result = mks.trend_test(
            x=values,
            t=dates,
            plot_path=plot_path,
            x_unit="mg/L",
            slope_scaling="year"
        )

        # 3. Print the full result
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
# Example 3: Non-Seasonal Trend Test with Timestamps

This example demonstrates how to perform a trend test on a time series that uses `datetime` objects and how to use the automatic slope scaling feature.

## The Python Script

The script generates 10 years of synthetic monthly data with a slight downward trend. It then calls `mks.trend_test`, passing a `pandas.DatetimeIndex` as the time vector `t`. Crucially, it also uses two new parameters:
-   `x_unit="mg/L"`: Specifies the units of the data.
-   `slope_scaling="year"`: Instructs the function to automatically scale the Sen's slope to "units per year".

```python
{code_block}
```

## Command Output

Running the script prints the full result object.

```
{output_str}
```

## Interpretation of Results

*   **Automatic Slope Scaling:** Because we set `slope_scaling="year"`, the `slope` field in the result is now automatically presented in **units per year**. The calculated slope of approximately -0.5 is consistent with the trend we built into the data.
*   **New Output Fields:**
    *   `slope`: This now contains the user-friendly scaled slope.
    *   `slope_units`: This field clearly states the units of the slope, e.g., `'mg/L per year'`.
    *   `slope_per_second`: The raw, unscaled slope in units per second is still available for users who need it.
*   **Significance:** The very low p-value and significant result (`h=True`) confirm that a statistically significant downward trend was detected.

### Plot Interpretation (`timestamp_trend_plot.png`)
The generated plot is also updated with the new information:
-   The statistics box now displays the scaled slope along with its new, descriptive units, making the plot much easier to interpret at a glance.

![Trend Plot](timestamp_trend_plot.png)

**Conclusion:** The new `x_unit` and `slope_scaling` parameters make it much easier to get an interpretable Sen's slope when working with `datetime` objects, removing the need for manual conversion.
"""

    # Write the README file
    readme_file_path = os.path.join(output_dir, 'README.md')
    with open(readme_file_path, 'w') as f:
        f.write(readme_content)

    print("Successfully generated README and plot for Example 3.")

if __name__ == '__main__':
    generate_readme()
