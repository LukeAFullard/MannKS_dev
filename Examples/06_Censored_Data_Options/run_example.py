import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/06_Censored_Data_Options'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'censored_options_output.txt')
robust_plot_file = os.path.join(output_dir, 'robust_method_plot.png')
lwp_plot_file = os.path.join(output_dir, 'lwp_method_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 6: Deep Dive into Censored Data Options ###")
    print("\nThis example compares the two methods for handling right-censored")
    print("data in the Mann-Kendall test: 'robust' (default) and 'lwp'.")
    print("The choice of method can impact the test's sensitivity and results,")
    print("especially when uncensored values are close to the censoring limit.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a dataset with an increasing trend and right-censored data.
    # The key feature is having uncensored values that are HIGHER than the
    # right-censored detection limit (e.g., 12 vs. '>10').
    dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2022), format='%Y'))
    values = ['5', '6', '7', '>10', '8', '9', '12', '>10', '14', '15', '18', '>20']

    print("\n--- Generated Data ---")
    df = pd.DataFrame({'date': dates, 'value': values})
    print(df.to_string())
    print("\nNote the right-censored values ('>10', '>20') and the uncensored")
    print("value '12' which is greater than the '>10' detection limit.")
    print("-" * 60)

    # --- 3. Pre-process the Censored Data ---
    print("\n--- 3. Pre-processing Data ---")
    # Convert the raw data into the required format
    prepared_data = mks.prepare_censored_data(values)
    print("Prepared data head:")
    print(prepared_data.head().to_string())
    print("-" * 60)


    # --- 4. Analysis with the 'robust' Method (Default) ---
    print("\n--- 4. Analysis with `mk_test_method='robust'` (Default) ---")
    print("The 'robust' method treats comparisons between an uncensored value and a")
    print("right-censored value as ambiguous if the uncensored value is greater")
    print("than the detection limit (e.g., 12 vs. >10). This comparison")
    print("contributes 0 to the S-statistic, making the test more conservative.")

    result_robust = mks.trend_test(
        x=prepared_data,
        t=dates,
        mk_test_method='robust', # This is the default
        plot_path=robust_plot_file
    )

    print("\nRobust Results:")
    print(result_robust)
    print(f"\nNote the p-value ({result_robust.p:.4f}) and the S-statistic ({result_robust.s}).")
    print(f"A plot has been saved to '{os.path.basename(robust_plot_file)}'.")
    print("-" * 60)


    # --- 5. Analysis with the 'lwp' Method ---
    print("\n--- 5. Analysis with `mk_test_method='lwp'` ---")
    print("The 'lwp' method emulates the LWP-TRENDS R script's heuristic.")
    print("It replaces all right-censored values with a single numeric value that")
    print("is slightly higher than the maximum uncensored value in the dataset.")
    print("This makes the test less conservative. For example, the comparison")
    print("12 vs. >10 is now treated as a decrease, contributing -1 to the")
    print("S-statistic, which can lead to a different final result.")


    result_lwp = mks.trend_test(
        x=prepared_data,
        t=dates,
        mk_test_method='lwp',
        plot_path=lwp_plot_file
    )

    print("\nLWP Results:")
    print(result_lwp)
    print(f"\nNote the p-value ({result_lwp.p:.4f}) and the S-statistic ({result_lwp.s}).")
    print("Compared to the 'robust' method, the S-statistic is different, leading")
    print("to a slightly different p-value and z-score.")
    print(f"A plot has been saved to '{os.path.basename(lwp_plot_file)}'.")
    print("-" * 60)

# Restore stdout
sys.stdout = original_stdout
print(f"Example 6 script finished. Output saved to {output_file}")
