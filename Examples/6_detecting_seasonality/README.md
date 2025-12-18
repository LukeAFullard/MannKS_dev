# Example 6: Detecting and Visualizing Seasonality

## Introduction

Is there a cyclical pattern in your data? Do values tend to be higher in the summer and lower in the winter, or vice-versa? Answering this question is a critical first step in time-series analysis. If a strong seasonal pattern exists, you should use a seasonal trend test (like `seasonal_trend_test`) to correctly identify the long-term trend. Ignoring seasonality can lead to incorrect conclusions.

The `MannKenSen` package provides two key functions for this purpose:
1.  `mks.check_seasonality()`: Performs a Kruskal-Wallis H-test to statistically determine if there's a significant difference between seasons.
2.  `mks.plot_seasonal_distribution()`: Creates a box plot to visually inspect the distribution of data for each season.

This example demonstrates how to use both.

## The Data

We will generate a 10-year monthly dataset with three components:
1.  A strong cosine-based seasonal pattern (higher values in winter, lower in summer).
2.  A slight long-term increasing trend.
3.  Random noise to make it more realistic.

Here is a sample of the first 5 rows:
```
        date      value
0 2010-01-31  31.989932
1 2010-02-28  29.563063
2 2010-03-31  24.965410
3 2010-04-30  15.548485
4 2010-05-31  10.785741
```

## Python Script (`run_example.py`)

The script below generates the data, runs the statistical test, and creates the visualization.

```python
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
```

## Results and Interpretation

The script produces the following output, confirming our expectations.

```text
### Example 6: Detecting and Visualizing Seasonality ###

Before performing a trend test, it's often crucial to determine
if your data has a seasonal pattern. A seasonal pattern can mask or
falsely indicate a long-term trend. The MannKenSen package provides
tools to both statistically test for and visualize seasonality.
------------------------------------------------------------

--- Generated Data ---
A 10-year monthly dataset was created with a clear seasonal cycle
(high in winter, low in summer) and a slight increasing trend.
Data head:
        date      value
0 2010-01-31  31.989932
1 2010-02-28  29.563063
2 2010-03-31  24.965410
3 2010-04-30  15.548485
4 2010-05-31  10.785741
------------------------------------------------------------

--- 3. Using `check_seasonality` ---
The `check_seasonality` function uses the Kruskal-Wallis H-test to
determine if there is a statistically significant difference between
the distributions of data for each season (in this case, months).

A low p-value (typically < 0.05) indicates significant seasonality.

Results:
Seasonality_Test(h_statistic=108.62772589574714, p_value=1.571434199990818e-18, is_seasonal=True, seasons_tested=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], seasons_skipped=[])

Conclusion: The p-value is very low, confirming the presence of
a significant seasonal pattern in the data.
------------------------------------------------------------

--- 4. Using `plot_seasonal_distribution` ---
A box plot is an excellent way to visualize seasonal patterns.
The `plot_seasonal_distribution` function creates a box plot showing
the data distribution for each month.

A box plot has been saved to 'seasonality_plot.png'.
This plot should visually confirm the cosine pattern we generated,
with higher values in winter months (1, 11, 12) and lower values
in summer months (6, 7).
------------------------------------------------------------
```

### Interpretation

1.  **Statistical Test:** The `check_seasonality` result shows an extremely small `p_value` (1.57e-18), which is far below the typical significance level of 0.05. This provides strong statistical evidence that the data distributions for different months are not the same, confirming a seasonal pattern.
2.  **Visualization:** The generated box plot provides clear visual confirmation of the statistical result.

### Generated Plot

![Seasonal Distribution Plot](./seasonality_plot.png)

The plot clearly shows the cyclical pattern: values are highest in the winter months (1, 12), lowest in the summer months (6, 7), and transition smoothly in between. This visual evidence, combined with the statistical test, gives us high confidence that a seasonal analysis is required for this dataset.
