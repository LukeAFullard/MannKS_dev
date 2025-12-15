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
