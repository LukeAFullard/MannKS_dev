import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/07_High_Censor_Rule'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'hicensor_output.txt')
original_plot_file = os.path.join(output_dir, 'original_data_plot.png')
hicensor_plot_file = os.path.join(output_dir, 'hicensor_rule_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 7: The High Censor Rule (`hicensor`) ###")
    print("\nThis example demonstrates the `hicensor` rule, a feature designed")
    print("to mitigate spurious trends that can arise from improvements in")
    print("laboratory detection limits over time.")
    print("\nIf detection limits decrease over a monitoring period, it can appear")
    print("as a decreasing trend in the data, even if the true concentration")
    print("has not changed. The `hicensor` rule corrects for this.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a dataset where the true concentration is stable, but the
    # detection limit improves (decreases) over time.
    dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2022), format='%Y'))
    values = ['<10', '<10', '<10', '<5', '<5', '<5', '<2', '<2', '<2', '<1', '<1', '<1']

    print("\n--- Generated Data ---")
    df = pd.DataFrame({'date': dates, 'value': values})
    print(df.to_string())
    print("\nNote that the data appears to have a strong decreasing trend, but")
    print("this is caused entirely by the improving (decreasing) detection limits.")
    print("-" * 60)

    # --- 3. Pre-process the Censored Data ---
    print("\n--- 3. Pre-processing Data ---")
    prepared_data = mks.prepare_censored_data(values)
    print("Prepared data head:")
    print(prepared_data.head().to_string())
    print("-" * 60)


    # --- 4. Analysis Without the `hicensor` Rule ---
    print("\n--- 4. Analysis Without the `hicensor` Rule (Default) ---")
    print("First, we analyze the data without applying the `hicensor` rule.")
    print("While a visual inspection of the raw values (10, 5, 2, 1) might suggest")
    print("a decreasing trend, the robust statistical test correctly handles the")
    print("comparisons between different censored levels (e.g., '<10' vs '<5') as")
    print("ambiguous (ties), resulting in a 'No Trend' finding.")

    result_original = mks.trend_test(
        x=prepared_data,
        t=dates,
        # No hicensor, using default 'robust' mk_test_method
        plot_path=original_plot_file
    )

    print("\nOriginal Results:")
    print(result_original)
    print(f"\nThe test correctly reports '{result_original.trend}'. This demonstrates that")
    print("the default statistical method is robust to these kinds of artifacts,")
    print("but the `hicensor` rule provides a more formal and transparent way")
    print("to handle the data.")
    print(f"A plot has been saved to '{os.path.basename(original_plot_file)}'.")
    print("-" * 60)


    # --- 5. Analysis With the `hicensor` Rule ---
    print("\n--- 5. Analysis with `hicensor=True` ---")
    print("Now, we apply the `hicensor` rule. This rule finds the highest")
    print("detection limit in the dataset (which is 10) and treats all values")
    print("(both censored and uncensored) below this limit as being censored at")
    print("that limit (i.e., '<10').")
    print("\nThis removes the artificial trend caused by the changing limits.")

    result_hicensor = mks.trend_test(
        x=prepared_data,
        t=dates,
        hicensor=True,
        plot_path=hicensor_plot_file
    )

    print("\n`hicensor` Results:")
    print(result_hicensor)
    print(f"\nWith the `hicensor` rule applied, the data becomes a series of tied")
    print("values ('<10'), and the test correctly reports 'No Trend'.")
    print("The analysis notes also indicate that the Sen slope could not be")
    print("calculated, which is expected for perfectly tied data.")
    print(f"A plot has been saved to '{os.path.basename(hicensor_plot_file)}'.")
    print("-" * 60)

# Restore stdout
sys.stdout = original_stdout
print(f"Example 7 script finished. Output saved to {output_file}")
