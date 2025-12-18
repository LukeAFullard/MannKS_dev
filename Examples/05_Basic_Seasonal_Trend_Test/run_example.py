import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory and file paths
output_dir = 'Examples/05_Basic_Seasonal_Trend_Test'
dist_plot_file = os.path.join(output_dir, 'seasonal_distribution_plot.png')
trend_plot_file = os.path.join(output_dir, 'seasonal_trend_plot.png')
readme_file = os.path.join(output_dir, 'README.md')


# --- 1. Generate Synthetic Seasonal Data ---
np.random.seed(42)
dates = pd.date_range(start='2010-01-01', end='2019-12-31', freq='ME')
n = len(dates)
month_numbers = dates.month
seasonal_pattern = 10 * np.cos(2 * np.pi * (month_numbers - 1) / 12) + 20
noise = np.random.normal(0, 2, n)
trend = np.linspace(0, 5, n)
values = seasonal_pattern + noise + trend

# --- 2. Statistically Check for Seasonality ---
seasonality_result = mks.check_seasonality(x_old=values, t_old=dates, season_type='month')

# --- 3. Visualize Seasonal Distribution ---
mks.plot_seasonal_distribution(
    x_old=values,
    t_old=dates,
    season_type='month',
    save_path=dist_plot_file
)

# --- 4. Perform Seasonal Trend Test ---
seasonal_trend_result = mks.seasonal_trend_test(
    x=values,
    t=dates,
    season_type='month',
    plot_path=trend_plot_file
)

# --- 5. Format Results and Generate README ---
seconds_in_year = 365.25 * 24 * 60 * 60
annual_slope = seasonal_trend_result.slope * seconds_in_year

seasonality_summary = f"""
- **Is Seasonal?:** {seasonality_result.is_seasonal}
- **P-value:** {seasonality_result.p_value:.2e}
- **H-statistic:** {seasonality_result.h_statistic:.2f}
"""

trend_summary = f"""
- **Trend Classification:** {seasonal_trend_result.classification}
- **P-value (p):** {seasonal_trend_result.p:.2e}
- **Annual Sen's Slope:** {annual_slope:.4f} (units per year)
- **Kendall's Tau:** {seasonal_trend_result.Tau:.4f}
"""

readme_content = f"""
# Example 5: Basic Seasonal Trend Test

This example demonstrates the standard workflow for analyzing time series data that has a seasonal pattern. Strong seasonality can mask or create spurious long-term trends, so it's essential to use a seasonal test to correctly identify the underlying trend.

The workflow involves three key steps:
1.  **Check for Seasonality:** Statistically determine if a seasonal pattern exists.
2.  **Visualize Seasonality:** Use a box plot to visually confirm the pattern.
3.  **Perform Seasonal Test:** If seasonality is present, use the `seasonal_trend_test` to find the long-term trend.

## Script: `run_example.py`
The script generates 10 years of synthetic monthly data containing a strong seasonal cycle (high in winter, low in summer) and a slight, underlying increasing trend. It then performs the three steps outlined above and dynamically generates this README with the captured results.

## Results

### 1. Seasonality Check
The `check_seasonality` function uses the Kruskal-Wallis H-test to check for significant differences between seasons. A low p-value indicates that a seasonal pattern is present.

{seasonality_summary}

The very low p-value confirms that the data is seasonal.

### 2. Seasonal Distribution Plot (`seasonal_distribution_plot.png`)
This box plot visualizes the data distribution for each month, clearly showing the cosine pattern that was generated in the synthetic data.
![Seasonal Distribution Plot](seasonal_distribution_plot.png)

### 3. Seasonal Trend Test
Since seasonality was confirmed, we use `seasonal_trend_test`. This function analyzes the trend for each season (month) individually before combining them, which correctly isolates the long-term trend from the seasonal cycle.

{trend_summary}

### Plot Interpretation (`seasonal_trend_plot.png`)
The final trend plot shows the raw data points with the calculated seasonal Sen's slope and its confidence intervals overlaid, confirming the slight increasing trend.
![Seasonal Trend Plot](seasonal_trend_plot.png)

**Conclusion:** This workflow—confirm, visualize, and then test for seasonal trend—is a robust method for analyzing seasonal time series data and correctly identifying long-term trends.
"""

with open(readme_file, 'w') as f:
    f.write(readme_content)

# Clean up the old text file if it exists
if os.path.exists(os.path.join(output_dir, 'seasonal_test_output.txt')):
    os.remove(os.path.join(output_dir, 'seasonal_test_output.txt'))

print("Successfully generated README and plots for Example 5.")
