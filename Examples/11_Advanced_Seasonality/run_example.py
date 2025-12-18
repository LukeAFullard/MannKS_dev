import numpy as np
import pandas as pd
import MannKenSen as mks
import os

# --- Define Paths ---
output_dir = 'Examples/11_Advanced_Seasonality'
dist_plot_file = os.path.join(output_dir, 'seasonal_distribution_plot.png')
trend_plot_file = os.path.join(output_dir, 'seasonal_trend_plot.png')
readme_file = os.path.join(output_dir, 'README.md')

# --- 1. Generate Data ---
np.random.seed(42)
dates = pd.date_range(start='2018-01-01', end='2020-12-31', freq='D')
n = len(dates)
day_of_week = dates.dayofweek
seasonal_pattern = np.where(day_of_week.isin([5, 6]), 25, 10) # Higher on weekends
noise = np.random.normal(0, 3, n)
trend = np.linspace(0, 15, n)
values = seasonal_pattern + noise + trend

# --- 2. Run Analyses ---
mks.plot_seasonal_distribution(
    x_old=values,
    t_old=dates,
    season_type='day_of_week',
    period=7,
    save_path=dist_plot_file
)
seasonal_trend_result = mks.seasonal_trend_test(
    x=values,
    t=dates,
    season_type='day_of_week',
    period=7,
    plot_path=trend_plot_file
)

# --- 3. Format Results and Generate README ---
annual_slope = seasonal_trend_result.slope * 365.25 * 24 * 60 * 60
result_summary = (
    "- **Classification:** {}\\n"
    "- **P-value:** {:.2e}\\n"
    "- **Annual Slope:** {:.4f}\\n"
).format(seasonal_trend_result.classification, seasonal_trend_result.p, annual_slope)

readme_content = """
# Example 11: Advanced Seasonality (Non-Monthly Data)

This example demonstrates the flexibility of `MannKenSen`'s seasonal analysis for non-monthly data, such as a weekly (`day_of_week`) pattern.

## Key Concepts
Seasonal analysis is not limited to monthly data. The `season_type` parameter in `seasonal_trend_test` and `plot_seasonal_distribution` allows analysis of any sub-annual pattern (e.g., weekly, quarterly) by correctly grouping the data.

## Script: `run_example.py`
The script generates a 3-year daily dataset with a strong weekly cycle (higher values on weekends) and an underlying increasing trend. It then visualizes the weekly pattern and performs a seasonal trend test using `season_type='day_of_week'`.

## Results
The test successfully isolates the long-term trend from the weekly cycle.
{}

### Seasonal Distribution Plot (`seasonal_distribution_plot.png`)
This plot clearly shows the weekly cycle, with higher values for day 5 (Saturday) and 6 (Sunday).
![Seasonal Distribution Plot](seasonal_distribution_plot.png)

### Seasonal Trend Plot (`seasonal_trend_plot.png`)
The trend plot shows the overall time series and correctly identifies the underlying increasing trend.
![Seasonal Trend Plot](seasonal_trend_plot.png)

**Conclusion:** The `season_type` parameter makes `seasonal_trend_test` a versatile tool for analyzing time series data with various cyclical patterns.
""".format(result_summary)

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'advanced_seasonality_output.txt')):
    os.remove(os.path.join(output_dir, 'advanced_seasonality_output.txt'))

print("Successfully generated README and plots for Example 11.")
