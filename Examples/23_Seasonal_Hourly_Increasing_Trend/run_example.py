
import os
import numpy as np
import pandas as pd
import MannKenSen

def generate_readme():
    """
    Generates the README.md file for this example, demonstrating a seasonal
    trend test on hourly data with an increasing trend.
    """
    # 1. Generate Synthetic Data
    np.random.seed(1)
    n_weeks = 4
    t = pd.to_datetime(pd.date_range(start='2023-01-01', periods=n_weeks * 7 * 24, freq='H'))

    # Create a long-term increasing trend
    long_term_trend = np.linspace(0, 15, len(t))

    # Create a strong diurnal (daily) pattern
    diurnal_cycle = 5 * np.sin(2 * np.pi * t.hour / 24)

    # Combine with noise
    noise = np.random.normal(0, 1.5, len(t))
    x = long_term_trend + diurnal_cycle + noise

    # 2. Run the Seasonal Trend Test
    plot_path = os.path.join(os.path.dirname(__file__), 'seasonal_hourly_trend.png')
    # For hourly data with a daily cycle, season_type is 'hour' and period is 24
    result = MannKenSen.seasonal_trend_test(x, t, season_type='hour', period=24, plot_path=plot_path)

    # 3. Format result for display
    result_str = (
        f"trend: {result.trend}\\n"
        f"h: {result.h}\\n"
        f"p: {result.p:.4f}\\n"
        f"z: {result.z:.4f}\\n"
        f"classification: {result.classification}\\n"
        f"slope: {result.slope * 365.25*24*60*60:.4f} (units/year)"
    )

    # --- Generate README ---
    readme_content = f"""
# Example 23: Seasonal Trend with Hourly Data (Increasing Trend)

The seasonal trend test can be applied to high-frequency data, such as hourly measurements, to identify long-term trends while accounting for daily (diurnal) cycles.

This example demonstrates how to configure the test for hourly data with a 24-hour seasonal period.

## 1. Data Generation

We generate 4 weeks of hourly data. The dataset is built with two key patterns:
1.  A steady long-term **increasing** trend.
2.  A strong **diurnal cycle**, simulating a repeating 24-hour pattern.

```python
import numpy as np
import pandas as pd
import MannKenSen

# 1. Generate Synthetic Data
np.random.seed(1)
n_weeks = 4
t = pd.to_datetime(pd.date_range(start='2023-01-01', periods=n_weeks * 7 * 24, freq='H'))

# Create a long-term increasing trend
long_term_trend = np.linspace(0, 15, len(t))

# Create a strong diurnal (daily) pattern
diurnal_cycle = 5 * np.sin(2 * np.pi * t.hour / 24)

# Combine with noise
noise = np.random.normal(0, 1.5, len(t))
x = long_term_trend + diurnal_cycle + noise

# 2. Run the Seasonal Trend Test
# For a daily cycle in hourly data, season_type='hour' and period=24
plot_path = 'seasonal_hourly_trend.png'
result = MannKenSen.seasonal_trend_test(x, t, season_type='hour', period=24, plot_path=plot_path)

print(result)
```

## 2. Results

The test is configured with `season_type='hour'` and `period=24`. It analyzes the trend for each hour of the day across the 4-week period. For example, it compares the data from 01:00 on day 1, 01:00 on day 2, and so on. The combined result correctly identifies the overall increasing trend.

```
{result_str}
```

The **'Highly Likely Increasing'** classification shows that the test successfully detected the underlying trend amidst the strong daily cycle.

## 3. Plot

The plot shows the data for all 24 seasons (hours). While the diurnal cycle is visible in the main plot (top left), each individual hourly subplot clearly shows the long-term increasing trend.

![Seasonal Hourly Trend Plot](seasonal_hourly_trend.png)
"""

    # Write to file
    filepath = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(filepath, 'w') as f:
        f.write(readme_content)
    print("Generated README.md and plot for Example 23.")

if __name__ == '__main__':
    generate_readme()
