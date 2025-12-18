import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/07_High_Censor_Rule'
original_plot_file = os.path.join(output_dir, 'original_data_plot.png')
hicensor_plot_file = os.path.join(output_dir, 'hicensor_rule_plot.png')
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate and Pre-process Data ---
np.random.seed(42)
dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2022), format='%Y'))
values = ['<10', '<10', '<10', '<5', '<5', '<5', '<2', '<2', '<2', '<1', '<1', '<1']
prepared_data = mks.prepare_censored_data(values)

# --- 2. Run Analyses ---
result_original = mks.trend_test(
    x=prepared_data,
    t=dates,
    plot_path=original_plot_file
)
result_hicensor = mks.trend_test(
    x=prepared_data,
    t=dates,
    hicensor=True,
    plot_path=hicensor_plot_file
)

# --- 3. Format Results and Generate README ---
original_summary = (
    "- **Classification:** {}\\n"
    "- **P-value:** {}\\n"
    "- **S-statistic:** {}\\n"
).format(result_original.classification, result_original.p, result_original.s)
hicensor_summary = (
    "- **Classification:** {}\\n"
    "- **P-value:** {}\\n"
    "- **S-statistic:** {}\\n"
).format(result_hicensor.classification, result_hicensor.p, result_hicensor.s)

readme_content = """
# Example 7: The High Censor Rule (`hicensor`)

This example demonstrates the `hicensor` rule, a feature for handling data where detection limits have improved over time, which can create a misleading "paper trend".

## Key Concepts

If a lab's detection limit improves (e.g., from `<10` to `<1`), data may appear to have a decreasing trend even if the true values are stable. The `hicensor` rule corrects for this. When `hicensor=True`, the function finds the highest detection limit (e.g., `10`) and treats all values below this limit as being censored at that limit (e.g., `<1` and `<5` both become `<10`).

## Script: `run_example.py`
The script generates a dataset where the recorded values decrease over time solely because the detection limit is improving. It analyzes the data twice: once without the `hicensor` rule and once with it.

## Results

### Analysis Without `hicensor` Rule
While a visual inspection of the raw values (10, 5, 2, 1) might suggest a trend, the robust statistical test correctly handles comparisons between different censored levels (e.g., `<10` vs. `<5`) as ambiguous ties.
{}
![Original Data Plot](original_data_plot.png)

### Analysis With `hicensor` Rule
Applying the `hicensor` rule formalizes the analysis by standardizing all data to the highest detection limit. This confirms the 'No Trend' result.
{}
![Hicensor Rule Plot](hicensor_rule_plot.png)

**Conclusion:** The `hicensor` rule is a key tool for validating trend analysis on long-term datasets where analytical methods may have changed.
""".format(original_summary, hicensor_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'hicensor_output.txt')):
    os.remove(os.path.join(output_dir, 'hicensor_output.txt'))

print("Successfully generated README and plots for Example 7.")
