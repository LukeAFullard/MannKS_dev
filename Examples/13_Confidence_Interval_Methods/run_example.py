import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/13_Confidence_Interval_Methods'
direct_plot_file = os.path.join(output_dir, 'direct_ci_plot.png')
lwp_plot_file = os.path.join(output_dir, 'lwp_ci_plot.png')
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate Data ---
np.random.seed(42)
dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2025), format='%Y'))
noise = np.random.normal(0, 2, len(dates))
trend = np.linspace(0, 10, len(dates))
values = 5 + trend + noise

# --- 2. Run Analyses ---
result_direct = mks.trend_test(
    x=values,
    t=dates,
    ci_method='direct',
    plot_path=direct_plot_file
)
result_lwp = mks.trend_test(
    x=values,
    t=dates,
    ci_method='lwp',
    plot_path=lwp_plot_file
)

# --- 3. Format Results and Generate README ---
s_in_y = 365.25 * 24 * 60 * 60
direct_summary = (
    "- **Annual Slope:** {:.4f}\\n"
    "- **Annual CI:** ({:.4f}, {:.4f})\\n"
).format(result_direct.slope * s_in_y, result_direct.lower_ci * s_in_y, result_direct.upper_ci * s_in_y)

lwp_summary = (
    "- **Annual Slope:** {:.4f}\\n"
    "- **Annual CI:** ({:.4f}, {:.4f})\\n"
).format(result_lwp.slope * s_in_y, result_lwp.lower_ci * s_in_y, result_lwp.upper_ci * s_in_y)

readme_content = """
# Example 13: Comparing Confidence Interval Methods

This example compares the two methods for calculating the confidence intervals (CI) for the Sen's slope: `'direct'` (default) and `'lwp'`.

## Key Concepts
-   `'direct'` **(Default):** Calculates the ranks of the CIs and rounds them to the nearest integer to directly index the sorted array of pairwise slopes.
-   `'lwp'`: Emulates the LWP-TRENDS R script by using linear interpolation between slopes to get a more precise CI estimate.

The choice of method does **not** affect the Sen's slope itself, only its confidence interval.

## Script: `run_example.py`
The script analyzes a simple linear dataset twice, once with each `ci_method`, and generates this README.

## Results
The Sen's slope is identical, but the confidence intervals are slightly different due to the calculation method.

### Direct CI Method (`ci_method='direct'`)
{}
![Direct CI Plot](direct_ci_plot.png)

### LWP CI Method (`ci_method='lwp'`)
{}
![LWP CI Plot](lwp_ci_plot.png)

**Conclusion:** The default `'direct'` method is generally sufficient. The `'lwp'` method is for users who need consistency with the LWP-TRENDS R script or prefer an interpolated result.
""".format(direct_summary, lwp_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'ci_methods_output.txt')):
    os.remove(os.path.join(output_dir, 'ci_methods_output.txt'))

print("Successfully generated README and plots for Example 13.")
