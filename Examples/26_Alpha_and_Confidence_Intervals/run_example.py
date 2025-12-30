
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import MannKS as mk
import io
import contextlib

# Ensure we are in the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def generate_readme():
    md_content = """# Example 26: Alpha and Confidence Intervals

This example demonstrates how the `alpha` parameter influences the **Confidence Intervals (CI)** of the Sen's slope and the final trend classification.

## The Role of Alpha
The `alpha` parameter sets the significance level for the confidence intervals.
*   **Lower `alpha` (e.g., 0.05):** corresponds to a **higher confidence level** (e.g., 95%). This produces a **wider** interval because we want to be more certain that the true slope lies within it.
*   **Higher `alpha` (e.g., 0.40):** corresponds to a **lower confidence level** (e.g., 60%). This produces a **narrower** interval because we are accepting a higher risk that the true slope is outside the range.

## Synthetic Data
We generate a dataset with a clear increasing trend and some random noise.
"""

    # 1. Generate Data
    np.random.seed(42)
    n = 30
    # Time: 2020-01-01 to 2022-06ish (monthly)
    dates = pd.date_range(start='2020-01-01', periods=n, freq='ME')

    # Value: Linear trend + Noise
    # Slope approx 2 units/year -> ~0.16 units/month
    values = np.linspace(10, 20, n) + np.random.normal(0, 2, n)

    df = pd.DataFrame({'Date': dates, 'Value': values})

    data_code = """
import numpy as np
import pandas as pd
import MannKS as mk

# Generate Data
np.random.seed(42)
n = 30
dates = pd.date_range(start='2020-01-01', periods=n, freq='ME')
values = np.linspace(10, 20, n) + np.random.normal(0, 2, n)
"""
    md_content += f"\n```python{data_code}```\n"

    alphas = [0.05, 0.20, 0.40]

    for alpha in alphas:
        md_content += f"\n## Analysis with alpha = {alpha}\n"
        md_content += f"This corresponds to a **{int((1-alpha)*100)}% Confidence Interval**.\n"

        plot_filename = f"plot_alpha_{alpha}.png"

        # Capture the output
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            result = mk.trend_test(
                x=values,
                t=dates,
                alpha=alpha,
                slope_scaling='year',
                plot_path=plot_filename
            )
            print(result) # Explicitly print the result to capture it
        output_str = f.getvalue()

        code_snippet = f"""
result = mk.trend_test(
    x=values,
    t=dates,
    alpha={alpha},
    slope_scaling='year',
    plot_path='{plot_filename}'
)
print(result)
"""
        md_content += f"\n```python{code_snippet}```\n"

        md_content += f"\n**Output:**\n```\n{output_str}```\n"

        # Add the plot
        md_content += f"\n![Trend Plot alpha={alpha}]({plot_filename})\n"

        # Explanation of the result
        slope = result.slope
        lower = result.lower_ci
        upper = result.upper_ci
        width = upper - lower

        md_content += f"\n**Interpretation:**\n"
        md_content += f"*   **Slope:** {slope:.4f} units/year\n"
        md_content += f"*   **Confidence Interval:** [{lower:.4f}, {upper:.4f}]\n"
        md_content += f"*   **Width of Interval:** {width:.4f}\n"
        md_content += f"\nNotice that the interval width for alpha={alpha} is **{'wider' if alpha == 0.05 else ('narrower' if alpha == 0.40 else 'intermediate')}** compared to the others.\n"

    # Write the README
    with open('README.md', 'w') as f:
        f.write(md_content)

    print("Example 26 completed. README.md and plots generated.")

if __name__ == "__main__":
    generate_readme()
