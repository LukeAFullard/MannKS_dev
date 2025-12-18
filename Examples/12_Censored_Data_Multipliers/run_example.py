import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/12_Censored_Data_Multipliers'
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate and Pre-process Data ---
np.random.seed(42)
dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2020), format='%Y'))
values = ['<2', '3', '<4', '5', '6', '7', '<8', '9', '10', '11']
prepared_data = mks.prepare_censored_data(values)

# --- 2. Run Analyses ---
result_default = mks.trend_test(x=prepared_data, t=dates)
result_custom = mks.trend_test(x=prepared_data, t=dates, lt_mult=0.75)

# --- 3. Format Results and Generate README ---
annual_slope_default = result_default.slope * 365.25 * 24 * 60 * 60
default_summary = (
    "- **Annual Slope:** {:.4f}\\n"
    "- **P-value:** {:.4f}\\n"
    "- **S-statistic:** {}\\n"
).format(annual_slope_default, result_default.p, result_default.s)

annual_slope_custom = result_custom.slope * 365.25 * 24 * 60 * 60
custom_summary = (
    "- **Annual Slope:** {:.4f}\\n"
    "- **P-value:** {:.4f}\\n"
    "- **S-statistic:** {}\\n"
).format(annual_slope_custom, result_custom.p, result_custom.s)

readme_content = """
# Example 12: The Impact of Censored Data Multipliers

This example explains the `lt_mult` and `gt_mult` parameters, which are used for sensitivity analysis of the Sen's slope calculation with censored data.

## Key Concepts
The Sen's slope calculation requires numeric values. For censored data, a substitution is made:
-   `lt_mult` (default `0.5`): A value like `'<10'` is replaced by `10 * lt_mult`.
-   `gt_mult` (default `1.0`): A value like `'>50'` is replaced by `50 * gt_mult`.

Changing these parameters **does not** affect the Mann-Kendall significance test (p-value, S-statistic), which is rank-based. It only affects the slope's magnitude.

## Script: `run_example.py`
The script analyzes a simple censored dataset twice: once with the default `lt_mult=0.5` and once with `lt_mult=0.75`.

## Results
The p-value and S-statistic are identical in both runs, as expected. The slope may or may not change depending on the data's structure.

### Default Multiplier (`lt_mult=0.5`)
{}

### Custom Multiplier (`lt_mult=0.75`)
{}

**Conclusion:** The `lt_mult` and `gt_mult` parameters are specialized tools for sensitivity analysis of the Sen's slope magnitude, without altering the trend's significance.
""".format(default_summary, custom_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'multipliers_output.txt')):
    os.remove(os.path.join(output_dir, 'multipliers_output.txt'))

print("Successfully generated README for Example 12.")
