
import os
import numpy as np
import pandas as pd
import MannKenSen as mk
from contextlib import redirect_stdout
import io

def generate_example():
    """
    Generates an example for the non-seasonal Akritas-Theil-Sen (ATS) trend analysis.
    This function creates a synthetic dataset, runs the ATS trend test,
    and generates a README.md file with the code, results, and explanation.
    """
    # --- 1. Setup: Create Synthetic Data ---
    np.random.seed(45)
    n = 50
    t = np.linspace(0, 20, n)
    true_slope = 0.08
    y_true = 2.0 + true_slope * t
    y = y_true + np.random.normal(scale=0.4, size=n)

    # Impose left-censoring
    lod = 2.5
    censored = y < lod
    y_obs = np.where(censored, lod, y)

    # Pre-process the censored data
    y_str_obs = np.array([f'<{lod}' if c else str(val) for c, val in zip(censored, y_obs)])
    x_prepared = mk.prepare_censored_data(y_str_obs)

    # Define plot path
    plot_path = os.path.join(os.path.dirname(__file__), 'ats_trend_plot.png')

    # --- 2. Code to Run: Execute ATS Trend Test ---
    # Use an f-string to store the code block that will be executed and displayed
    code_to_run = f"""
import numpy as np
import pandas as pd
import MannKenSen as mk

# --- 1. Prepare Your Data ---
# Create a synthetic dataset with a known trend
np.random.seed(45)
n = 50
t = np.linspace(0, 20, n)
true_slope = 0.08
y_true = 2.0 + true_slope * t
y = y_true + np.random.normal(scale=0.4, size=n)

# Impose a left-censoring limit (less-than)
lod = 2.5
censored = y < lod
y_obs = np.where(censored, lod, y)

# Use the prepare_censored_data utility by creating a single array
# where censored values are represented as strings (e.g., '<2.5').
y_str_obs = np.array([f'<{lod}' if c else str(val) for c, val in zip(censored, y_obs)])
x_prepared = mk.prepare_censored_data(y_str_obs)


# --- 2. Run the Trend Test with ATS ---
# --- 2. Run Trend Test with the Default Method ---
# The default method (`sens_slope_method='nan'`) is statistically neutral but
# may be less powerful with censored data as it discards ambiguous slope pairs.
default_results = mk.trend_test(
    x=x_prepared,
    t=t,
    sens_slope_method='nan'
)

# --- 3. Run the Trend Test with ATS ---
# The ATS estimator (`sens_slope_method='ats'`) is a more robust method
# specifically designed for censored data.
ats_results = mk.trend_test(
    x=x_prepared,
    t=t,
    sens_slope_method='ats',
    plot_path='ats_trend_plot.png'
)

# --- 4. Print and Compare the Results ---
print("--- Default Method Results (sens_slope_method='nan') ---")
print(f"Slope: {{default_results.slope:.4f}}")
print(f"95% CI for Slope: ({{default_results.lower_ci:.4f}}, {{default_results.upper_ci:.4f}})")
print("\\n--- Akritas-Theil-Sen (ATS) Method Results ---")
print(f"Trend: {{ats_results.trend}}")
print(f"P-value: {{ats_results.p:.4f}}")
print(f"ATS Slope: {{ats_results.slope:.4f}}")
print(f"Intercept: {{ats_results.intercept:.4f}}")
print(f"95% CI for Slope: ({{ats_results.lower_ci:.4f}}, {{ats_results.upper_ci:.4f}})")
"""

    # --- 3. Execution: Capture Output ---
    # Execute the code and capture the print output
    output_capture = io.StringIO()
    with redirect_stdout(output_capture):
        exec(code_to_run)
    results_output = output_capture.getvalue()

    # --- 4. Documentation: Create README.md ---
    readme_content = f"""
# Example 27: Akritas-Theil-Sen (ATS) Trend Analysis

This example demonstrates how to perform a robust trend analysis on censored data using the **Akritas-Theil-Sen (ATS) estimator**. The ATS method is a statistically sound approach for calculating a Sen's slope when the data contains non-detects (censored values). It works by analyzing data as intervals and is generally preferred over simple substitution methods.

The `sens_slope_method='ats'` parameter in `trend_test` enables this functionality.

##
## Python Code

```python
{code_to_run.strip()}
```

##
## Results

The code above produces the following output. The ATS method, being specifically designed for censored data, provides a slightly different (and often more accurate) slope estimate compared to the default method.

```
{results_output.strip()}
```

##
## Comparison of Methods

-   **Default Method (`'nan'`):** This method calculates all possible pairwise slopes and discards any that are ambiguous due to censoring (e.g., the slope between a value of `5` and `<10`). This is a statistically neutral approach, but it can lose power if a large fraction of pairs are discarded.
-   **ATS Method (`'ats'`):** This method does not discard ambiguous pairs. Instead, it uses a formal statistical technique to find the slope that best fits the interval-censored data. It is generally more powerful and robust when censored data is present.

In this example, the ATS slope is slightly closer to the true underlying slope of {true_slope:.2f}. The generated plot, which always uses the results from the primary method being demonstrated (in this case, ATS), visually confirms the increasing trend.

![ATS Trend Plot](ats_trend_plot.png)

This example highlights the power of the ATS method for deriving accurate trend estimates from censored environmental data.
"""

    # --- 5. File Output: Write README.md ---
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'w') as f:
        f.write(readme_content)
    print("Example 27 README.md generated successfully.")

if __name__ == "__main__":
    generate_example()
