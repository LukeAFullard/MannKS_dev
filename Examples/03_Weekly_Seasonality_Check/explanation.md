# Example 3: Checking for Seasonality

A common workflow in trend analysis is to first determine if a seasonal pattern exists in your data before deciding to use a seasonal trend test. This example demonstrates how to use the `check_seasonality` function to statistically verify a seasonal pattern and then proceed with `seasonal_trend_test`.

We will simulate daily data with a clear weekly pattern (e.g., lower values on weekends).

## Steps

1.  **Generate Synthetic Data**: We create five years of daily data. A strong weekly pattern is added by assigning different values for weekdays versus weekends. No long-term trend is added.
2.  **Check for Seasonality**: We use the `check_seasonality` function to test the hypothesis that there is a significant difference between the days of the week.
3.  **Perform Seasonal Trend Analysis**: Based on the confirmation of seasonality, we proceed with the `seasonal_trend_test`. It now automatically classifies the trend and returns data quality notes.
4.  **Review the Output**: We print and examine the results from both functions.

## Python Code (`weekly_seasonality.py`)

The full Python script for this example is shown below.

```python
import numpy as np
import pandas as pd
from MannKenSen import check_seasonality, seasonal_trend_test

def main():
    """
    Generate daily data with a weekly pattern and demonstrate how to use
    `check_seasonality` to detect this pattern before trend analysis.
    """
    # 1. Generate Synthetic Data with a Weekly Pattern
    n_years = 5
    t = pd.to_datetime(pd.date_range(start='2018-01-01', periods=365 * n_years, freq='D'))

    day_of_week = t.dayofweek
    weekly_pattern = np.array([-15 if day in (5, 6) else 5 for day in day_of_week])
    noise = np.random.normal(0, 4, len(t))
    x = 100 + weekly_pattern + noise

    # 2. Check for Seasonality
    print("--- Checking for Weekly Seasonality ---")
    seasonality_result = check_seasonality(x, t, season_type='day_of_week', period=7)

    print(f"Seasonality detected: {seasonality_result.is_seasonal}")
    print(f"P-value: {seasonality_result.p_value:.4f}")

    # 3. Perform Seasonal Trend Analysis
    print("\n--- Seasonal Trend Analysis ---")
    plot_path = "Examples/03_Weekly_Seasonality_Check/weekly_seasonality_plot.png"
    trend_result = seasonal_trend_test(x, t, season_type='day_of_week', period=7, plot_path=plot_path)

    # 4. Print the Trend Results
    print(f"  Classification: {trend_result.classification}")
    print(f"  Trend: {trend_result.trend}")
    print(f"  P-value: {trend_result.p:.4f}")
    print(f"  Slope: {trend_result.slope:.4f} ({trend_result.lower_ci:.4f}, {trend_result.upper_ci:.4f})")
    print(f"  Analysis Notes: {trend_result.analysis_notes if trend_result.analysis_notes else 'None'}")
    print(f"\n  Plot saved to: {plot_path}")

if __name__ == "__main__":
    main()
```

## Results

### Seasonality Check

The `check_seasonality` function returns `is_seasonal: True` with a very low p-value, confirming our hypothesis that a significant weekly pattern exists in the data.

```
--- Checking for Weekly Seasonality ---
Seasonality detected: True
P-value: 0.0000
```

### Seasonal Trend Analysis

The `seasonal_trend_test` correctly identifies that there is **"No Trend"** in the data over time, which aligns with how we generated the data. It also returns an `Analysis Note` warning that the Sen's slope calculation was influenced by tied values, which is expected given the repeating nature of our synthetic weekly pattern.

```
--- Seasonal Trend Analysis ---
  Classification: No Trend
  Trend: no trend
  P-value: 0.6841
  Slope: 0.0000 (-0.0000, 0.0000)
  Analysis Notes: ['WARNING: Sen slope based on tied non-censored values']

  Plot saved to: Examples/03_Weekly_Seasonality_Check/weekly_seasonality_plot.png
```

### Generated Plot

The plot shows the daily data points, which clearly exhibit a repeating weekly pattern. The calculated trend line is nearly flat, visually confirming the "No Trend" result.

![Weekly Seasonality Plot](weekly_seasonality_plot.png)
