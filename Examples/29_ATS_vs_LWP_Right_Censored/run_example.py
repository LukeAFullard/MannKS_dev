
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import MannKenSen as mk
from contextlib import redirect_stdout
import io

def generate_example():
    """
    Generates an example comparing ATS, LWP, and Default methods on Right-Censored data.
    """
    # --- 1. Setup: Create Synthetic Data ---
    np.random.seed(101)
    n = 50
    t = np.arange(n)
    true_slope = 0.5
    intercept = 10.0

    # Generate data: increasing trend
    y_true = intercept + true_slope * t
    noise = np.random.normal(scale=2.0, size=n)
    y = y_true + noise

    # Impose Right Censoring: Values > 30 are censored
    # This simulates a sensor saturation or an upper detection limit
    limit = 30.0
    censored = y > limit

    # Create the censored string representation
    # For right censoring, LWP uses "measured value" if detected, or "> limit" if censored.
    # Note: prepare_censored_data expects '>30.0' for right censoring.
    y_str = []
    for val, is_cen in zip(y, censored):
        if is_cen:
            y_str.append(f">{limit}")
        else:
            y_str.append(str(val))
    y_str = np.array(y_str)

    x_prepared = mk.prepare_censored_data(y_str)

    # Plot path
    plot_path = os.path.join(os.path.dirname(__file__), 'right_censored_comparison.png')

    # --- 2. Code Block to Display ---
    # Note: We hardcode 'limit' value in the f-string for clarity in the example
    code_to_run = f"""
import numpy as np
import pandas as pd
import MannKenSen as mk
import matplotlib.pyplot as plt

# --- 1. Prepare Right-Censored Data ---
# A dataset where values grow until they hit an upper limit (saturation)
np.random.seed(101)
n = 50
t = np.arange(n)
true_slope = 0.5
y = 10.0 + true_slope * t + np.random.normal(scale=2.0, size=n)

limit = 30.0
censored = y > limit
y_str = [f">{{limit}}" if c else str(v) for c, v in zip(censored, y)]
x_prepared = mk.prepare_censored_data(y_str)

print(f"True Slope: {{true_slope}}")
print(f"Percent Censored: {{np.mean(censored)*100:.1f}}%")

# --- 2. Run Trend Tests with Different Methods ---

# Method A: Default ('nan')
# Treats indeterminate pairs (e.g. >30 vs >30) as ties/NaN.
res_default = mk.trend_test(x_prepared, t, sens_slope_method='nan')

# Method B: LWP Emulation ('lwp')
# Replaces >30 with 30 * 1.1 = 33.0, then computes standard Sen's slope.
res_lwp = mk.trend_test(x_prepared, t, sens_slope_method='lwp', gt_mult=1.1)

# Method C: Akritas-Theil-Sen ('ats')
# Uses interval arithmetic (30 to infinity) to solve for the slope.
res_ats = mk.trend_test(x_prepared, t, sens_slope_method='ats')

# --- 3. Compare Results ---
print(f"\\nDefault Slope: {{res_default.slope:.4f}}")
print(f"LWP Slope:     {{res_lwp.slope:.4f}}")
print(f"ATS Slope:     {{res_ats.slope:.4f}}")

# --- 4. Plotting ---
plt.figure(figsize=(10, 6))
# Plot data points
plt.scatter(t[~censored], y[~censored], c='blue', label='Detected')
plt.scatter(t[censored], [limit]*np.sum(censored), c='red', marker='^', label='Right Censored (>30)')

# Plot trend lines
def get_line(res, t_vec):
    if pd.isna(res.slope): return None
    # For visualization, use the calculated intercept and slope
    return res.intercept + res.slope * t_vec

plt.plot(t, 10.0 + true_slope * t, 'k--', alpha=0.5, label='True Trend')
plt.plot(t, get_line(res_default, t), 'g-', label=f'Default (s={{res_default.slope:.3f}})')
plt.plot(t, get_line(res_lwp, t), 'm-', label=f'LWP (s={{res_lwp.slope:.3f}})')
plt.plot(t, get_line(res_ats, t), 'b-', linewidth=2, label=f'ATS (s={{res_ats.slope:.3f}})')

plt.legend()
plt.title('Comparison of Sen Slope Methods on Right-Censored Data')
plt.xlabel('Time')
plt.ylabel('Value')
plt.grid(True, alpha=0.3)
plt.savefig('right_censored_comparison.png')
"""

    # --- 3. Execution ---
    output_capture = io.StringIO()
    with redirect_stdout(output_capture):
        exec(code_to_run)
    results_output = output_capture.getvalue()

    # --- 4. Documentation ---
    readme_content = f"""
# Example 29: ATS vs LWP for Right Censored Data

This example compares three different methods for calculating the Sen's slope on **right-censored** data (e.g., values that exceed a measurement limit).

**The Challenge:**
Right censoring is common in environmental data (e.g., "greater than range").
- **Default (`nan`)**: Ignores ambiguous pairs. If many high values are censored, we lose information about the magnitude of the increase at the top end.
- **LWP (`lwp`)**: Substitutes right-censored values with `Limit * 1.1`. This is a heuristic. If the true values are much higher than `Limit * 1.1`, this method will **underestimate** the slope.
- **ATS (`ats`)**: Treats right-censored values as intervals $[Limit, \\infty)$. It finds the slope that best aligns the residuals, even using the "infinite" upper bounds.

##
## Python Code

```python
{code_to_run.strip()}
```

##
## Results

```
{results_output.strip()}
```

##
## Interpretation

*   **True Slope:** 0.5
*   **Default:** Likely underestimates or is unstable because it discards comparisons involving the highest values.
*   **LWP:** Effectively "caps" the rising trend at `Limit * 1.1` (33.0). Since the true data keeps rising well past 33.0, the LWP slope is pulled down (flattened) towards zero as time goes on.
*   **ATS:** Correctly identifies that the trend continues upward, even though the specific values are unknown. It typically provides the estimate closest to the true slope.

![Right Censored Comparison](right_censored_comparison.png)
"""

    with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'w') as f:
        f.write(readme_content)
    print("Example 29 README.md generated successfully.")

if __name__ == "__main__":
    generate_example()
