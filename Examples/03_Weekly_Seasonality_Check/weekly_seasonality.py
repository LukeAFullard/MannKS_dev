import numpy as np
import pandas as pd
from MannKenSen import check_seasonality, seasonal_trend_test

def main():
    """
    Generate daily data with a clear weekly pattern (lower values on weekends)
    and demonstrate how to use `check_seasonality` to detect this pattern.
    """
    # 1. Generate Synthetic Data with a Weekly Pattern
    n_years = 5
    t = pd.to_datetime(pd.date_range(start='2018-01-01', periods=365 * n_years, freq='D'))

    # Create a strong weekly pattern (lower values on weekends)
    day_of_week = t.dayofweek  # Monday=0, Sunday=6
    weekly_pattern = np.array([-15 if day in (5, 6) else 5 for day in day_of_week])

    # Add some noise but no long-term trend for this example
    noise = np.random.normal(0, 4, len(t))
    x = 100 + weekly_pattern + noise

    # 2. Check for Seasonality
    # We hypothesize a 'day_of_week' pattern, so we set the `season_type`
    # and provide the corresponding `period=7`.
    print("--- Checking for Weekly Seasonality ---")
    seasonality_result = check_seasonality(x, t, season_type='day_of_week', period=7)

    print(f"Seasonality detected: {seasonality_result.is_seasonal}")
    print(f"P-value of Kruskal-Wallis test: {seasonality_result.p_value:.4f}")
    if seasonality_result.is_seasonal:
        print("\nThe low p-value confirms a statistically significant difference between the days of the week.")

    # 3. Optional: Analyze the trend
    # Although we didn't add a trend, we can still run the test.
    # We would expect a 'no trend' result.
    print("\n--- Seasonal Trend Analysis (expecting no trend) ---")
    plot_path = "Examples/03_Weekly_Seasonality_Check/weekly_seasonality_plot.png"
    trend_result = seasonal_trend_test(x, t, season_type='day_of_week', period=7, plot_path=plot_path)

    print(f"  Trend Result: {trend_result.trend}")


if __name__ == "__main__":
    main()
