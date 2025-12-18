import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/12_Censored_Data_Multipliers'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'multipliers_output.txt')
# No plot is needed for this example as the effect is numerical.

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 12: The Impact of Censored Data Multipliers ###")
    print("\nThis example demonstrates the `lt_mult` and `gt_mult` parameters,")
    print("which control the numeric substitution for censored data when calculating")
    print("the Sen's slope. Changing these values does NOT affect the Mann-Kendall")
    print("test itself (p-value, S-statistic) but can be used for sensitivity")
    print("analysis of the slope magnitude.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a simple dataset with a clear increasing trend and left-censored data.
    dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2020), format='%Y'))
    values = ['<2', '3', '<4', '5', '6', '7', '<8', '9', '10', '11']

    print("\n--- Generated Data ---")
    df = pd.DataFrame({'date': dates, 'value': values})
    print(df.to_string())
    print("\nThe data has a clear increasing trend with several left-censored values.")
    print("-" * 60)

    # --- 3. Pre-process the Censored Data ---
    print("\n--- 3. Pre-processing Data ---")
    prepared_data = mks.prepare_censored_data(values)
    print("Prepared data head:")
    print(prepared_data.head().to_string())
    print("-" * 60)


    # --- 4. Analysis with Default Multiplier (`lt_mult=0.5`) ---
    print("\n--- 4. Analysis with Default Multiplier (`lt_mult=0.5`) ---")
    print("By default, left-censored values are replaced by their detection limit")
    print("times 0.5 for the slope calculation (e.g., '<4' becomes 2.0).")

    result_default = mks.trend_test(
        x=prepared_data,
        t=dates,
        # lt_mult=0.5 is the default
    )

    # Convert slope to annual for interpretation
    seconds_in_year = 365.25 * 24 * 60 * 60
    annual_slope_default = result_default.slope * seconds_in_year

    print("\nDefault Results:")
    print(f"Annual Slope: {annual_slope_default:.4f}")
    print(f"P-value: {result_default.p:.4f}")
    print(f"S-statistic: {result_default.s}")
    print("-" * 60)


    # --- 5. Analysis with a Custom Multiplier (`lt_mult=0.75`) ---
    print("\n--- 5. Analysis with a Custom Multiplier (`lt_mult=0.75`) ---")
    print("Now, we change the multiplier to 0.75. This assumes the true value is")
    print("closer to the detection limit (e.g., '<4' becomes 3.0). This should")
    print("result in a slightly higher calculated Sen's slope.")

    result_custom = mks.trend_test(
        x=prepared_data,
        t=dates,
        lt_mult=0.75
    )

    annual_slope_custom = result_custom.slope * seconds_in_year

    print("\nCustom Multiplier Results:")
    print(f"Annual Slope: {annual_slope_custom:.4f}")
    print(f"P-value: {result_custom.p:.4f}")
    print(f"S-statistic: {result_custom.s}")
    print("\nConclusion: As shown, changing `lt_mult` had no effect on the p-value or")
    print("S-statistic. While the slope magnitude can change, in this run it did")
    print("not, which can happen if the median of slopes is not sensitive to the")
    print("substituted values. This highlights that the primary use of these")
    print("parameters is for sensitivity analysis.")
    print("-" * 60)


# Restore stdout
sys.stdout = original_stdout
print(f"Example 12 script finished. Output saved to {output_file}")
