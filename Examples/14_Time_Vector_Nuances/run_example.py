import numpy as np
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/14_Time_Vector_Nuances'
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate Data ---
np.random.seed(42)
years = np.arange(2010, 2020)
noise = np.random.normal(0, 0.5, len(years))
trend = np.linspace(0, 5, len(years))
values = 10 + trend + noise

# --- 2. Run Analyses ---
t_integer = np.arange(len(years))
result_integer = mks.trend_test(x=values, t=t_integer)

t_years = years
result_years = mks.trend_test(x=values, t=t_years)

# --- 3. Format Results and Generate README ---
integer_summary = (
    "- **Slope:** {:.4f} (units per index)\\n"
    "- **P-value:** {:.4f}\\n"
    "- **S-statistic:** {}\\n"
).format(result_integer.slope, result_integer.p, result_integer.s)

year_summary = (
    "- **Slope:** {:.4f} (units per year)\\n"
    "- **P-value:** {:.4f}\\n"
    "- **S-statistic:** {}\\n"
).format(result_years.slope, result_years.p, result_years.s)

readme_content = """
# Example 14: Time Vector Nuances (Numeric Data)

This example highlights that for numeric time vectors, the units of the Sen's slope are determined by the units of the time vector `t`.

## Key Concepts
The Mann-Kendall test for significance (p, s, z) is rank-based and is **not** affected by the scale of the time vector. However, the Sen's slope calculation is `(y2 - y1) / (t2 - t1)`, so its units depend directly on the units of `t`.

-   If `t = [0, 1, 2, ...]`, the slope is in **units per index step**.
-   If `t = [2010, 2011, ...]` the slope is in **units per year**.

## Script: `run_example.py`
The script analyzes the same data twice: once with a simple integer time vector and once with a vector of years.

## Results
The p-value and S-statistic are identical, but the slope's magnitude is different and more interpretable when using a meaningful time vector.

### Analysis with `t = [0, 1, 2, ...]`
{}

### Analysis with `t = [2010, 2011, ...]`
{}

**Conclusion:** Always use a time vector with meaningful units (e.g., years) when possible to ensure the Sen's slope is directly interpretable.
""".format(integer_summary, year_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'time_vector_output.txt')):
    os.remove(os.path.join(output_dir, 'time_vector_output.txt'))

print("Successfully generated README for Example 14.")
