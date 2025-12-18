import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/08_Aggregation_Tied_Clustered_Data'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'aggregation_output.txt')
plot_file = os.path.join(output_dir, 'aggregation_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 8: Aggregation for Tied and Clustered Data ###")
    print("\nThis example demonstrates how to handle datasets with tied timestamps")
    print("or high-frequency clusters of data using temporal aggregation.")
    print("Such data can bias the Sen's slope calculation by giving more")
    print("weight to periods with more measurements.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a dataset with non-uniform sampling to show the need for aggregation.
    # We have a clear increasing trend, but with clusters of data.
    dates = pd.to_datetime([
        '2010-07-01', '2011-07-01', '2012-07-01',
        '2013-03-01', '2013-03-05', '2013-03-10', '2013-03-15', # Clustered data
        '2014-06-15', '2014-06-15', # Tied timestamps
        '2015-07-01', '2016-07-01', '2017-07-01', '2018-07-01', '2019-07-01'
    ])
    values = np.array([5, 5.5, 6, 6.2, 6.3, 6.1, 6.4, 7, 6.8, 7.5, 8, 8.2, 8.5, 9])

    print("\n--- Generated Data ---")
    # Use a DataFrame for clear printing
    df = pd.DataFrame({'date': dates, 'value': values})
    print(df.to_string())
    print("\nNote the clustered data in 2013 and the tied timestamps in 2014.")
    print("-" * 60)

    # --- 3. Analysis Without Aggregation ---
    print("\n--- 3. Analysis Without Aggregation (agg_method='none') ---")
    print("First, we run the analysis without aggregation. The presence of tied")
    print("timestamps will be flagged in the 'analysis_notes', as this can")
    print("potentially bias the Sen's Slope calculation.")

    # Run the test. No plot is generated for the non-aggregated version here.
    result_no_agg = mks.trend_test(x=values, t=dates, agg_method='none')

    print("\nResults:")
    print(result_no_agg)
    print("\nThe analysis note correctly identifies that the Sen's slope may be")
    print("affected by the tied timestamps.")
    print("-" * 60)

    # --- 4. Analysis With Aggregation ---
    print("\n--- 4. Analysis With Aggregation (agg_method='median', agg_period='year') ---")
    print("Now, we apply annual aggregation. The function will calculate the")
    print("median value for each year and then perform the trend test on the")
    print("aggregated data. This provides a more robust trend estimate by ensuring")
    print("each year contributes equally to the analysis.")

    # The `agg_period` parameter is required when `t` contains datetimes
    result_agg = mks.trend_test(
        x=values,
        t=dates,
        agg_method='median',
        agg_period='year', # Aggregate to one value per year
        plot_path=plot_file
    )

    print("\nResults:")
    print(result_agg)

    # The slope is returned in units/sec for datetime inputs. Convert to units/year.
    seconds_in_year = 365.25 * 24 * 60 * 60
    annual_slope = result_agg.slope * seconds_in_year
    annual_lower_ci = result_agg.lower_ci * seconds_in_year
    annual_upper_ci = result_agg.upper_ci * seconds_in_year

    print(f"\nAnnual Slope: {annual_slope:.4f}")
    print(f"Annual CI: ({annual_lower_ci:.4f}, {annual_upper_ci:.4f})")

    print("\nWith aggregation, the analysis note about tied data is gone, and the")
    print("resulting slope and p-value are based on a temporally balanced dataset.")
    print(f"A plot has been saved to '{os.path.basename(plot_file)}'.")
    print("-" * 60)

# Restore stdout
sys.stdout = original_stdout
print(f"Example 8 script finished. Output saved to {output_file}")
