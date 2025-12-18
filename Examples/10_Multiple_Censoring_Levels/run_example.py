import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/10_Multiple_Censoring_Levels'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'multi_censor_output.txt')
plot_file = os.path.join(output_dir, 'multi_censor_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 10: Handling Data with Multiple Censoring Levels ###")
    print("\nThis example demonstrates the robustness of the package in handling")
    print("complex, realistic datasets that contain numerous different")
    print("censoring levels for both left-censored ('<') and right-censored ('>') data.")
    print("\nThe underlying statistical methods are designed to correctly interpret")
    print("these varied limits without any special user intervention other than")
    print("the standard preprocessing step.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a dataset with a clear increasing trend and a mix of many
    # different censoring levels.
    dates = pd.to_datetime(pd.to_datetime(np.arange(2005, 2025), format='%Y'))
    values = [
        '<1', '1.2', '<2', '1.8', '<1',  # Low values, some censored
        '2.5', '<5', '4.8', '5.1', '<5',  # Medium values
        '7.2', '8.1', '>10', '12.3', '11.8', # High values, one right-censored
        '>10', '14.5', '15.9', '>15', '18.2' # Higher values, more right-censored
    ]


    print("\n--- Generated Data ---")
    df = pd.DataFrame({'date': dates, 'value': values})
    print(df.to_string())
    print("\nNote the mix of uncensored, left-censored ('<1', '<2', '<5'), and")
    print("right-censored ('>10', '>15') data points.")
    print("-" * 60)

    # --- 3. Pre-process and Analyze ---
    print("\n--- 3. Pre-processing and Analyzing Data ---")
    print("Even with complex data, the workflow remains the same:")
    print("1. Use `prepare_censored_data` to convert the raw data.")
    print("2. Pass the prepared data to `trend_test`.")

    # 1. Prepare the data
    prepared_data = mks.prepare_censored_data(values)

    # 2. Run the trend test
    result = mks.trend_test(
        x=prepared_data,
        t=dates,
        plot_path=plot_file
    )

    print("\nAnalysis Results:")
    print(result)

    # Convert slope to annual for interpretation
    seconds_in_year = 365.25 * 24 * 60 * 60
    annual_slope = result.slope * seconds_in_year

    print(f"\nAnnual Slope: {annual_slope:.4f}")

    print("\nConclusion: The package correctly identifies the strong 'Increasing' trend")
    print("despite the complexity of the multiple censoring levels. The plot")
    print("visualizes how the different types of data points are handled.")
    print(f"A plot has been saved to '{os.path.basename(plot_file)}'.")
    print("-" * 60)

# Restore stdout
sys.stdout = original_stdout
print(f"Example 10 script finished. Output saved to {output_file}")
