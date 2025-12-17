import numpy as np
import pandas as pd
from MannKenSen import check_seasonality, seasonal_trend_test

def main():
    """
    Validation script for weekly seasonality.

    This script generates synthetic daily data with a weekly pattern, saves it to
    a CSV file, and then runs the Python `seasonal_trend_test` to analyze it.
    The results can be compared with the output of the corresponding R script.
    """
    # 1. Generate Synthetic Data with a Weekly Pattern
    n_years = 5
    t = pd.to_datetime(pd.date_range(start='2018-01-01', periods=365 * n_years, freq='D'))

    day_of_week = t.dayofweek
    weekly_pattern = np.array([-15 if day in (5, 6) else 5 for day in day_of_week])
    np.random.seed(42) # Set seed for reproducibility
    noise = np.random.normal(0, 4, len(t))
    x = 100 + weekly_pattern + noise

    # Save data for R validation
    df = pd.DataFrame({'Date': t, 'Value': x})
    df.to_csv('validation/03_Weekly_Seasonality_Check/validation_data.csv', index=False)

    # 2. Check for Seasonality
    print("--- Python: Checking for Weekly Seasonality ---")
    seasonality_result = check_seasonality(x, t, season_type='day_of_week', period=7)
    print(f"  Seasonality detected: {seasonality_result.is_seasonal}")
    print(f"  P-value: {seasonality_result.p_value:.4f}")

    # 3. Perform Seasonal Trend Analysis
    print("\n--- Python: Seasonal Trend Analysis ---")
    plot_path = "validation/03_Weekly_Seasonality_Check/weekly_seasonality_plot.png"
    trend_result = seasonal_trend_test(x, t, season_type='day_of_week', period=7, plot_path=plot_path)

    # 4. Print the Trend Results
    print(f"  Classification: {trend_result.classification}")
    print(f"  P-value: {trend_result.p:.4f}")
    print(f"  Slope: {trend_result.slope:.4f} ({trend_result.lower_ci:.4f}, {trend_result.upper_ci:.4f})")

if __name__ == "__main__":
    main()
