"""
Example 30: Rolling Trend Analysis

This example demonstrates how to perform a rolling trend analysis to visualize
how a trend evolves over time, and how to compare trends before and after a specific date.
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import MannKS as mk

# Ensure output directory exists
output_dir = os.path.dirname(__file__)

# --- 1. Generate Synthetic Data ---
# We simulate 30 years of monthly data (360 points)
# Years 0-15: Flat/No trend
# Years 15-30: Increasing trend
np.random.seed(42)
dates = pd.date_range('1990-01-01', periods=360, freq='ME')
n = len(dates)

# Base values with noise
values = np.random.normal(10, 2, n)

# Add trend starting from index 180 (Year 2005)
# Slope of 0.5 per year -> ~0.04 per month
trend_start_idx = 180
values[trend_start_idx:] += np.linspace(0, 7.5, n - trend_start_idx)

# Create DataFrame
df = pd.DataFrame({'Date': dates, 'Value': values})

# --- 2. Rolling Trend Analysis ---
# We use a 10-year window, sliding by 1 year.
# This helps identify when the trend starts to emerge.
print("Running rolling trend analysis...")
rolling_results = mk.rolling_trend_test(
    x=df['Value'],
    t=df['Date'],
    window='10Y',
    step='1Y',
    min_size=30,  # Require at least 30 months of data per window
    slope_scaling='year',
    continuous_confidence=True
)

# Display first few rows of results
print("\nRolling Analysis Results (Head):")
print(rolling_results[['window_center', 'slope', 'C', 'classification']].head())

# --- 3. Visualization ---
print("\nGenerating rolling trend plot...")
plot_path = os.path.join(output_dir, 'rolling_trend_analysis.png')
mk.plot_rolling_trend(
    rolling_results,
    data=df,
    time_col='Date',
    value_col='Value',
    highlight_significant=True,
    show_global_trend=True,
    save_path=plot_path,
    figsize=(12, 10)
)
print(f"Plot saved to {plot_path}")

# --- 4. Before/After Comparison ---
# Let's verify the change point around 2005 (when we injected the trend).
breakpoint = pd.Timestamp('2005-01-01')
print(f"\nComparing periods before and after {breakpoint.date()}...")

comparison = mk.compare_periods(
    x=df['Value'],
    t=df['Date'],
    breakpoint=breakpoint,
    slope_scaling='year'
)

print(f"Slope Before: {comparison['before'].slope:.4f}")
print(f"Slope After:  {comparison['after'].slope:.4f}")
print(f"Slope Difference: {comparison['slope_difference']:.4f}")
print(f"Significant Change (Non-overlapping CIs): {comparison['significant_change']}")

# Generate README
readme_content = f"""
# Example 30: Rolling Trend Analysis

This example demonstrates the `rolling_trend_test` feature, which applies the Mann-Kendall test and Sen's slope estimator over a moving window. This is crucial for non-stationary data where trends may start, stop, or reverse over time.

## Scenario
We generated 30 years of synthetic monthly data (1990-2020).
- **1990-2005:** No trend (random noise).
- **2005-2020:** Increasing trend.

## Rolling Analysis
We applied a **10-year rolling window** sliding by **1 year**.

### Python Code
```python
import pandas as pd
import numpy as np
import MannKS as mk

# [Data Generation Code Omitted - See run_example.py]

# Run Rolling Test
rolling_results = mk.rolling_trend_test(
    x=df['Value'],
    t=df['Date'],
    window='10Y',
    step='1Y',
    slope_scaling='year'
)

# Visualize
mk.plot_rolling_trend(
    rolling_results,
    data=df,
    time_col='Date',
    value_col='Value',
    save_path='rolling_trend_analysis.png'
)
```

### Results Table (Snippet)
The rolling analysis detects the transition. Early windows (purely in the 1990-2005 range) should show no trend, while later windows capture the increase.

{rolling_results[['window_center', 'slope', 'C', 'classification']].to_markdown(index=False)}

### Visualization
![Rolling Trend Plot](rolling_trend_analysis.png)

## Change Point Verification
We manually compared the periods before and after 2005 using `compare_periods`.

- **Slope Before 2005:** {comparison['before'].slope:.4f}
- **Slope After 2005:** {comparison['after'].slope:.4f}
- **Significant Change:** {comparison['significant_change']}

The test correctly identifies a significant shift in the trend trajectory.
"""

with open(os.path.join(output_dir, 'README.md'), 'w') as f:
    f.write(readme_content)

print("\nREADME.md generated.")
