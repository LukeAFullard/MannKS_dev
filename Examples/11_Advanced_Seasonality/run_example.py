import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/11_Advanced_Seasonality'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'advanced_seasonality_output.txt')
dist_plot_file = os.path.join(output_dir, 'seasonal_distribution_plot.png')
trend_plot_file = os.path.join(output_dir, 'seasonal_trend_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 11: Advanced Seasonality (Non-Monthly Data) ###")
    print("\nThis example demonstrates that seasonal analysis is not limited to")
    print("monthly data. The `seasonal_trend_test` function can analyze any")
    print("sub-annual pattern (e.g., daily, weekly, quarterly) by using the")
    print("`season_type` parameter.")
    print("\nHere, we will analyze data with a strong weekly pattern (e.g., weekday vs.")
    print("weekend effects) to find the underlying long-term trend.")
    print("-" * 60)

    # --- 2. Generate Synthetic Weekly Data ---
    # Create a 3-year dataset with daily data points.
    dates = pd.date_range(start='2018-01-01', end='2020-12-31', freq='D')
    n = len(dates)

    # Create a weekly pattern (higher values on weekends).
    # Day 0 is Monday, 5 and 6 are Saturday and Sunday.
    day_of_week = dates.dayofweek
    seasonal_pattern = np.where(day_of_week.isin([5, 6]), 25, 10)

    # Add some random noise
    noise = np.random.normal(0, 3, n)

    # Add a clear increasing long-term trend
    trend = np.linspace(0, 15, n)

    # Combine the components
    values = seasonal_pattern + noise + trend

    print("\n--- Generated Data ---")
    print("A 3-year daily dataset was created with a strong weekly cycle")
    print("(high on weekends, low on weekdays) and an increasing trend.")
    df = pd.DataFrame({'date': dates, 'value': values})
    print("Data head:")
    print(df.head().to_string())
    print("-" * 60)

    # --- 3. Visualize the Weekly Pattern ---
    print("\n--- 3. Visualize with `plot_seasonal_distribution` ---")
    print("We can create a box plot to visualize the distribution for each day")
    print("of the week, which should clearly show the weekend effect.")

    mks.plot_seasonal_distribution(
        x_old=values,
        t_old=dates,
        season_type='day_of_week',
        period=7,
        save_path=dist_plot_file
    )
    print(f"\nA box plot has been saved to '{os.path.basename(dist_plot_file)}'.")
    print("Note: 0=Monday, 1=Tuesday, ..., 6=Sunday.")
    print("-" * 60)


    # --- 4. Perform Seasonal Trend Test on Weekly Data ---
    print("\n--- 4. Using `seasonal_trend_test` with `season_type='day_of_week'` ---")
    print("By specifying `season_type='day_of_week'`, the test analyzes the trend")
    print("for all Mondays, all Tuesdays, etc., separately, then combines the")
    print("results. This correctly isolates the long-term trend from the weekly cycle.")

    seasonal_trend_result = mks.seasonal_trend_test(
        x=values,
        t=dates,
        season_type='day_of_week',
        period=7,
        plot_path=trend_plot_file
    )

    print("\nResults:")
    print(seasonal_trend_result)

    # Convert slope to annual for interpretation
    seconds_in_year = 365.25 * 24 * 60 * 60
    annual_slope = seasonal_trend_result.slope * seconds_in_year

    print(f"\nAnnual Slope: {annual_slope:.4f}")
    print("\nConclusion: The test correctly identifies the strong 'Increasing' trend")
    print("even with the powerful weekly pattern in the data.")
    print(f"A trend plot has been saved to '{os.path.basename(trend_plot_file)}'.")
    print("-" * 60)


# Restore stdout
sys.stdout = original_stdout
print(f"Example 11 script finished. Output saved to {output_file}")
