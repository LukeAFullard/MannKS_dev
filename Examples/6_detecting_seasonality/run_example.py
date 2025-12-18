import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/6_detecting_seasonality'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'seasonality_output.txt')
plot_file = os.path.join(output_dir, 'seasonality_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 6: Detecting and Visualizing Seasonality ###")
    print("\nBefore performing a trend test, it's often crucial to determine")
    print("if your data has a seasonal pattern. A seasonal pattern can mask or")
    print("falsely indicate a long-term trend. The MannKenSen package provides")
    print("tools to both statistically test for and visualize seasonality.")
    print("-" * 60)

    # --- 2. Generate Synthetic Seasonal Data ---
    # Create a 10-year dataset with monthly data points.
    dates = pd.date_range(start='2010-01-01', end='2019-12-31', freq='ME')
    n = len(dates)

    # Create a seasonal pattern (e.g., higher values in summer, lower in winter)
    # The month number (1-12) is used to create a cyclical pattern.
    month_numbers = dates.month
    seasonal_pattern = 10 * np.cos(2 * np.pi * (month_numbers - 1) / 12) + 20

    # Add some random noise to make it more realistic
    noise = np.random.normal(0, 2, n)

    # Add a slight increasing long-term trend
    trend = np.linspace(0, 5, n)

    # Combine the components
    values = seasonal_pattern + noise + trend

    print("\n--- Generated Data ---")
    print("A 10-year monthly dataset was created with a clear seasonal cycle")
    print("(high in winter, low in summer) and a slight increasing trend.")
    df = pd.DataFrame({'date': dates, 'value': values})
    print("Data head:")
    print(df.head().to_string())
    print("-" * 60)

    # --- 3. Statistically Check for Seasonality ---
    print("\n--- 3. Using `check_seasonality` ---")
    print("The `check_seasonality` function uses the Kruskal-Wallis H-test to")
    print("determine if there is a statistically significant difference between")
    print("the distributions of data for each season (in this case, months).")
    print("\nA low p-value (typically < 0.05) indicates significant seasonality.")

    seasonality_result = mks.check_seasonality(x_old=values, t_old=dates, season_type='month')

    print("\nResults:")
    print(seasonality_result)

    if seasonality_result.is_seasonal:
        print("\nConclusion: The p-value is very low, confirming the presence of")
        print("a significant seasonal pattern in the data.")
    else:
        print("\nConclusion: No significant seasonal pattern was detected.")
    print("-" * 60)

    # --- 4. Visualize Seasonal Distribution ---
    print("\n--- 4. Using `plot_seasonal_distribution` ---")
    print("A box plot is an excellent way to visualize seasonal patterns.")
    print("The `plot_seasonal_distribution` function creates a box plot showing")
    print("the data distribution for each month.")

    mks.plot_seasonal_distribution(
        x_old=values,
        t_old=dates,
        season_type='month',
        save_path=plot_file
    )

    print(f"\nA box plot has been saved to '{os.path.basename(plot_file)}'.")
    print("This plot should visually confirm the cosine pattern we generated,")
    print("with higher values in winter months (1, 11, 12) and lower values")
    print("in summer months (6, 7).")
    print("-" * 60)

# Restore stdout
sys.stdout = original_stdout
print(f"Example 6 script finished. Output saved to {output_file}")
