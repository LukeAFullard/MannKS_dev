import os
import io
import contextlib
import numpy as np
import pandas as pd
import MannKS as mk
import matplotlib.pyplot as plt

# --- 1. Define the Example Code as a String ---
example_code = """
import numpy as np
import pandas as pd
import MannKS as mk
import matplotlib.pyplot as plt

# 1. Generate Autocorrelated Data (AR1 Process)
# Autocorrelation (serial dependence) is common in environmental data.
# A high value today often means a high value tomorrow, even without a long-term trend.
# Standard Mann-Kendall assumes independence and often produces FALSE POSITIVES
# (finding a 'trend' that is just persistence).

np.random.seed(42)
n = 100
t = pd.date_range('2000-01-01', periods=n, freq='ME')

# Generate AR(1) noise: x[t] = 0.8 * x[t-1] + noise
# High correlation (phi=0.8) makes the data "wander" and look like a trend.
x = np.zeros(n)
x[0] = np.random.normal(0, 1)
for i in range(1, n):
    x[i] = 0.8 * x[i-1] + np.random.normal(0, 1)

# Add a very weak trend (or no trend)
trend_signal = 0.0 * np.arange(n)
x = x + trend_signal

print(f"Data generated: {n} points with AR(1) coefficient ~0.8 and NO trend.")

# 2. Run Standard Trend Test (The "Naive" Approach)
print("\\n--- Test 1: Standard Mann-Kendall (Assuming Independence) ---")
result_std = mk.trend_test(
    x, t,
    autocorr_method='none',
    slope_scaling='year',
    plot_path='plot_std.png'
)

print(f"Trend: {result_std.trend}")
print(f"p-value: {result_std.p:.4f}")
print(f"Significant? {result_std.h}")
print("Note: If p < 0.05, this is a False Positive caused by autocorrelation.")


# 3. Run Block Bootstrap Test (The "Robust" Approach)
# The block bootstrap method preserves the autocorrelation structure by resampling
# blocks of data instead of individual points. This correctly estimates the
# significance even when data is dependent.
print("\\n--- Test 2: Block Bootstrap Mann-Kendall ---")
result_boot = mk.trend_test(
    x, t,
    autocorr_method='block_bootstrap',
    n_bootstrap=1000,
    slope_scaling='year',
    plot_path='plot_boot.png'
)

print(f"Trend: {result_boot.trend}")
print(f"p-value: {result_boot.p:.4f}")
print(f"Significant? {result_boot.h}")
print(f"Autocorrelation (ACF1): {result_boot.acf1:.3f}")
print(f"Block Size Used: {result_boot.block_size_used}")


# 4. Seasonal Block Bootstrap
# For seasonal data, we must bootstrap 'cycles' (e.g., years) to preserve seasonality.
print("\\n--- Test 3: Seasonal Block Bootstrap ---")

# Generate seasonal data with autocorrelation between years
n_years = 20
dates_seas = pd.date_range('2000-01-01', periods=n_years*12, freq='ME')
seasonal_pattern = np.tile(np.sin(np.linspace(0, 2*np.pi, 12)), n_years)

# Autocorrelated noise (inter-annual persistence)
noise_seas = np.zeros(n_years*12)
current_noise = 0
for i in range(n_years*12):
    current_noise = 0.7 * current_noise + np.random.normal(0, 1)
    noise_seas[i] = current_noise

x_seas = seasonal_pattern + noise_seas # No trend

result_seas = mk.seasonal_trend_test(
    x_seas, dates_seas,
    period=12,
    autocorr_method='block_bootstrap',
    slope_scaling='year',
    plot_path='plot_seas_boot.png'
)

print(f"Seasonal Trend: {result_seas.trend}")
print(f"p-value: {result_seas.p:.4f}")
print(f"Significant? {result_seas.h}")
print(f"Block Size Used: {result_seas.block_size_used} (cycles)")
"""

# --- 2. Execute the Code and Capture Output ---
output_buffer = io.StringIO()

script_dir = os.path.dirname(os.path.abspath(__file__))
original_cwd = os.getcwd()
os.chdir(script_dir)

try:
    with contextlib.redirect_stdout(output_buffer):
        local_scope = {}
        exec(example_code, globals(), local_scope)
finally:
    os.chdir(original_cwd)

captured_output = output_buffer.getvalue()

# --- 3. Generate the README.md ---
readme_content = f"""
# Example 29: Block Bootstrap for Autocorrelation

## The "Why": The Autocorrelation Problem
Standard Mann-Kendall tests assume that data points are **independent** (like rolling a die).
However, environmental data is often **autocorrelated**:
*   A hot day is likely to be followed by another hot day.
*   A drought year might influence groundwater levels for the next year.

**The Danger:** Autocorrelation reduces the "effective" amount of information in your data. If you ignore it, the standard test underestimates the variance and often reports a **statistically significant trend when none exists (False Positive).**

**The Solution:** The **Block Bootstrap** method. Instead of shuffling individual data points (which destroys correlation), it shuffles **blocks** of contiguous data. This preserves the correlation structure while generating a valid null distribution for testing.

## The "How": Code Walkthrough

We will simulate data with strong autocorrelation (AR1 process) but **no trend**, and compare the standard test vs. the bootstrap test.

### Step 1: Python Code
```python
{example_code.strip()}
```

### Step 2: Text Output
```text
{captured_output}
```

## Interpreting the Results

### 1. The False Positive (Standard Test)
*   In Test 1, the standard Mann-Kendall test likely reported a low p-value (e.g., $p < 0.05$) and claimed a significant trend.
*   **Why?** The data "wandered" up or down due to persistence (memory), and the test mistook this random wandering for a deterministic trend.

### 2. The Correction (Block Bootstrap)
*   In Test 2, `autocorr_method='block_bootstrap'` was used.
*   The package automatically calculated the autocorrelation (ACF1) and determined an optimal block size.
*   The resulting p-value should be higher (non-significant), correctly identifying that there is **no trend**.

### 3. Seasonal Application
*   In Test 3, we applied this to seasonal data.
*   For seasonal tests, the "block" unit is the **cycle** (e.g., a year). The bootstrap resamples entire years to ensure that the seasonal pattern (January to December) remains intact, while accounting for correlation *between* years.

## Visual Results

### Standard (Naive) Test
![Standard Plot](plot_std.png)
*Notice how the red trend line might look convincing, but the data points are clustered above/below the line for long periods? That's autocorrelation.*

### Bootstrap (Robust) Test
![Bootstrap Plot](plot_boot.png)
*The trend line and data are the same, but the statistical conclusion (p-value) in the title/results is now correct.*

## Key Takeaway
If you suspect your data has serial correlation (common in daily or monthly environmental data), use `autocorr_method='block_bootstrap'` (or `'auto'`) to avoid false positives.
"""

with open(os.path.join(script_dir, 'README.md'), 'w') as f:
    f.write(readme_content)

print("Example 29 generated successfully.")
