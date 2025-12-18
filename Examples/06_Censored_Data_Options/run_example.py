import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/06_Censored_Data_Options'
robust_plot_file = os.path.join(output_dir, 'robust_method_plot.png')
lwp_plot_file = os.path.join(output_dir, 'lwp_method_plot.png')
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate Synthetic Data ---
np.random.seed(42)
dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2022), format='%Y'))
values = ['5', '6', '7', '>10', '8', '9', '12', '>10', '14', '15', '18', '>20']

# --- 2. Pre-process the Censored Data ---
prepared_data = mks.prepare_censored_data(values)

# --- 3. Run Analyses ---
result_robust = mks.trend_test(
    x=prepared_data,
    t=dates,
    mk_test_method='robust',
    plot_path=robust_plot_file
)
result_lwp = mks.trend_test(
    x=prepared_data,
    t=dates,
    mk_test_method='lwp',
    plot_path=lwp_plot_file
)

# --- 4. Format Results and Generate README ---
robust_summary = f"""
- **Classification:** {result_robust.classification}
- **P-value:** {result_robust.p:.4f}
- **S-statistic:** {result_robust.s}
- **Sen's Slope:** {result_robust.slope * 365.25 * 24 * 60 * 60:.4f}
"""
lwp_summary = f"""
- **Classification:** {result_lwp.classification}
- **P-value:** {result_lwp.p:.4f}
- **S-statistic:** {result_lwp.s}
- **Sen's Slope:** {result_lwp.slope * 365.25 * 24 * 60 * 60:.4f}
"""

readme_content = f"""
# Example 6: Deep Dive into Censored Data Options

This example compares the two methods for handling right-censored data in the Mann-Kendall test: `'robust'` (the default) and `'lwp'`. The choice of method can impact the test's sensitivity, especially when uncensored values are near the censoring limit.

## Key Concepts

-   **`mk_test_method='robust'` (Default):** This conservative approach treats a comparison between an uncensored value and a right-censored value as ambiguous (contributing 0 to the S-statistic) if the uncensored value is greater than the detection limit (e.g., `12` vs. `>10`).
-   **`mk_test_method='lwp'`:** This method emulates the LWP-TRENDS R script. It replaces all right-censored values with a number slightly higher than the maximum uncensored value, making the test less conservative. For example, the comparison `12` vs. `>10` is now treated as a decrease (-1 to S-statistic).

## Script: `run_example.py`
The script generates data with a key feature: an uncensored value (`12`) that is greater than a right-censored limit (`>10`). It runs the trend test using both methods and generates this README.

## Results

### Robust Method (`mk_test_method='robust'`)
{robust_summary}
![Robust Method Plot](robust_method_plot.png)

### LWP Method (`mk_test_method='lwp'`)
{lwp_summary}
![LWP Method Plot](lwp_method_plot.png)

### Interpretation
The `'robust'` method produces a lower S-statistic because it treats the ambiguous `12` vs. `>10` comparison as a tie. The `'lwp'` method treats this as a decrease, resulting in a different S-statistic and p-value.

**Conclusion:** The `'robust'` method is generally recommended. The `'lwp'` method is for users who need to replicate results from the LWP-TRENDS R script.
"""

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'censored_options_output.txt')):
    os.remove(os.path.join(output_dir, 'censored_options_output.txt'))

print("Successfully generated README and plots for Example 6.")
