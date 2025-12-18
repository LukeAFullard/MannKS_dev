import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/10_Multiple_Censoring_Levels'
plot_file = os.path.join(output_dir, 'multi_censor_plot.png')
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate and Pre-process Data ---
np.random.seed(42)
dates = pd.to_datetime(pd.to_datetime(np.arange(2005, 2025), format='%Y'))
values = [
    '<1', '1.2', '<2', '1.8', '<1',
    '2.5', '<5', '4.8', '5.1', '<5',
    '7.2', '8.1', '>10', '12.3', '11.8',
    '>10', '14.5', '15.9', '>15', '18.2'
]
prepared_data = mks.prepare_censored_data(values)

# --- 2. Run Analysis ---
result = mks.trend_test(
    x=prepared_data,
    t=dates,
    plot_path=plot_file
)

# --- 3. Format Results and Generate README ---
annual_slope = result.slope * 365.25 * 24 * 60 * 60
result_summary = (
    "- **Classification:** {}\\n"
    "- **P-value:** {:.2e}\\n"
    "- **Annual Slope:** {:.4f}\\n"
    "- **Proportion Censored:** {:.2%}\\n"
).format(result.classification, result.p, annual_slope, result.prop_censored)

readme_content = """
# Example 10: Handling Data with Multiple Censoring Levels

This example demonstrates the robustness of `MannKenSen` in handling complex, realistic datasets that contain numerous different censoring levels.

## Key Concepts
Real-world data often has a mix of censoring types (e.g., `<1`, `<5`, `>50`). The statistical engine in `MannKenSen` is designed to handle this complexity automatically. The standard workflow of `prepare_censored_data` followed by `trend_test` is sufficient. The test correctly interprets the relationships between all pairs of values, whether they are censored or not.

## Script: `run_example.py`
The script generates a synthetic dataset with an increasing trend and a complex mix of left-censored (`<1`, `<2`, `<5`) and right-censored (`>10`, `>15`) data. It runs the standard analysis workflow and generates this README.

## Results
The analysis correctly identifies the strong increasing trend despite the complex data.
{}

### Analysis Plot (`multi_censor_plot.png`)
The plot visualizes the complex data, using different markers for uncensored (circles), left-censored (downward triangles), and right-censored (upward triangles) data points.
![Multi-Censor Plot](multi_censor_plot.png)

**Conclusion:** `MannKenSen` is a robust tool for handling complex, messy, real-world censored data without requiring special configuration.
""".format(result_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'multi_censor_output.txt')):
    os.remove(os.path.join(output_dir, 'multi_censor_output.txt'))

print("Successfully generated README and plot for Example 10.")
