
import os
import numpy as np
import pandas as pd
import MannKenSen as mk
from contextlib import redirect_stdout
import io

def generate_example():
    """
    Generates an example for the seasonal Akritas-Theil-Sen (ATS) trend analysis.
    This function creates a synthetic seasonal dataset, runs the ATS trend test,
    and generates a README.md file with the code, results, and explanation.
    """
    # --- 1. Setup: Create Synthetic Seasonal Data ---
    np.random.seed(42)
    n_years = 10
    n_seasons = 4
    n = n_years * n_seasons

    # Create a datetime index
    t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='QS-DEC'))

    # Create a true underlying trend
    true_slope_per_year = 0.1
    time_numeric_years = np.linspace(0, n_years, n, endpoint=False)
    y_true = 1.0 + true_slope_per_year * time_numeric_years

    # Add seasonality and noise
    seasonality = np.tile([0, 1.5, 0.5, 2.0], n_years)
    y = y_true + seasonality + np.random.normal(scale=0.2, size=n)

    # Impose left-censoring
    lod = 2.0
    censored = y < lod
    y_str_obs = np.array([f'<{lod}' if c else str(val) for c, val in zip(censored, y)])
    x_prepared = mk.prepare_censored_data(y_str_obs)

    # Define plot path
    plot_path = os.path.join(os.path.dirname(__file__), 'seasonal_ats_trend_plot.png')

    # --- 2. Code to Run: Execute Seasonal ATS Trend Test ---
    # Use an f-string to store the code block that will be executed and displayed
    code_to_run = f"""
import numpy as np
import pandas as pd
import MannKenSen as mk

# --- 1. Prepare Your Seasonal Data ---
np.random.seed(42)
n_years = 10
n_seasons = 4
n = n_years * n_seasons

# Create a datetime index for the time vector `t`
t = pd.to_datetime(pd.date_range(start='2000-01-01', periods=n, freq='QS-DEC'))

# Create a synthetic dataset with a known trend, seasonality, and noise
true_slope_per_year = 0.1
time_numeric_years = np.linspace(0, n_years, n, endpoint=False)
y_true = 1.0 + true_slope_per_year * time_numeric_years
seasonality = np.tile([0, 1.5, 0.5, 2.0], n_years)
y = y_true + seasonality + np.random.normal(scale=0.2, size=n)

# Impose a left-censoring limit
lod = 2.0
censored = y < lod
y_str_obs = np.array([f'<{lod}' if c else str(val) for c, val in zip(censored, y)])
x_prepared = mk.prepare_censored_data(y_str_obs)

# --- 2. Run the Seasonal Trend Test with ATS ---
# --- 2. Run Trend Test with the Default Method ---
default_results = mk.seasonal_trend_test(
    x=x_prepared,
    t=t,
    period=n_seasons,
    season_type='quarter',
    sens_slope_method='nan',
    slope_scaling='year'
)

# --- 3. Run the Seasonal Trend Test with ATS ---
ats_results = mk.seasonal_trend_test(
    x=x_prepared,
    t=t,
    period=n_seasons,
    season_type='quarter',
    sens_slope_method='ats',
    slope_scaling='year',
    plot_path='seasonal_ats_trend_plot.png'
)

# --- 4. Print and Compare the Results ---
print("--- Default Method Results (sens_slope_method='nan') ---")
print(f"Slope (per year): {{default_results.slope:.4f}}")
print(f"95% CI for Slope: ({{default_results.lower_ci:.4f}}, {{default_results.upper_ci:.4f}})")
print("\\n--- Akritas-Theil-Sen (ATS) Method Results ---")
print(f"Trend: {{ats_results.trend}}")
print(f"P-value: {{ats_results.p:.4f}}")
print(f"Overall ATS Slope (per year): {{ats_results.slope:.4f}}")
print(f"Intercept: {{ats_results.intercept:.4f}}")
print(f"95% CI for Slope: ({{ats_results.lower_ci:.4f}}, {{ats_results.upper_ci:.4f}})")
"""

    # --- 3. Execution: Capture Output ---
    output_capture = io.StringIO()
    with redirect_stdout(output_capture):
        exec(code_to_run)
    results_output = output_capture.getvalue()

    # --- 4. Documentation: Create README.md ---
    readme_content = f"""
# Example 28: Seasonal Akritas-Theil-Sen (ATS) Trend Analysis

This example demonstrates how to use the **Akritas-Theil-Sen (ATS) estimator** for a **seasonal** trend analysis on censored data.

When `sens_slope_method='ats'` is used with `seasonal_trend_test`, the function calculates a single, overall ATS slope for the entire dataset. This approach is consistent with the `censeaken` R script and provides a robust, unified trend estimate across all seasons. It also computes bootstrap confidence intervals for this overall slope.

##
## Python Code

```python
{code_to_run.strip()}
```

##
## Results

The code produces the following output. As with the non-seasonal case, the robust ATS method provides a different slope estimate than the default method.

```
{results_output.strip()}
```

##
## Comparison of Methods

-   **Default Method (`'nan'`):** For seasonal data, this method calculates all pairwise slopes *within each season*, discards ambiguous pairs, and then takes the median of all collected slopes.
-   **ATS Method (`'ats'`):** For seasonal data, this method calculates a *single* overall ATS slope across the entire dataset at once. This is consistent with the `censeaken.R` script and provides a unified, robust trend estimate.

In this example, both methods detect a significant increasing trend. The plot shows the final trend line generated by the ATS method.

![Seasonal ATS Trend Plot](seasonal_ats_trend_plot.png)

This example shows how to apply the powerful ATS method to seasonal, censored data to obtain a single, reliable estimate of the overall trend.
"""

    # --- 5. File Output: Write README.md ---
    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'w') as f:
        f.write(readme_content)
    print("Example 28 README.md generated successfully.")

if __name__ == "__main__":
    generate_example()
