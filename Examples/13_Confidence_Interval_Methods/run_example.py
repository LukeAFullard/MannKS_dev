import numpy as np
import pandas as pd
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/13_Confidence_Interval_Methods'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'ci_methods_output.txt')
direct_plot_file = os.path.join(output_dir, 'direct_ci_plot.png')
lwp_plot_file = os.path.join(output_dir, 'lwp_ci_plot.png')

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 13: Comparing Confidence Interval Methods ###")
    print("\nThis example compares the two methods for calculating the confidence")
    print("intervals (CI) for the Sen's slope: 'direct' (default) and 'lwp'.")
    print("The choice of method affects how the confidence limits are selected")
    print("from the distribution of all pairwise slopes.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a simple dataset with a clear trend.
    dates = pd.to_datetime(pd.to_datetime(np.arange(2010, 2025), format='%Y'))
    noise = np.random.normal(0, 2, len(dates))
    trend = np.linspace(0, 10, len(dates))
    values = 5 + trend + noise

    print("\n--- Generated Data ---")
    df = pd.DataFrame({'date': dates, 'value': values})
    print("Generated a simple linear dataset with some noise.")
    print("Data head:")
    print(df.head().to_string())
    print("-" * 60)

    # --- 3. Analysis with 'direct' CI Method (Default) ---
    print("\n--- 3. Analysis with `ci_method='direct'` (Default) ---")
    print("The 'direct' method calculates the ranks of the upper and lower CIs")
    print("and rounds them to the nearest integer to directly index the sorted")
    print("array of pairwise slopes. It is fast and straightforward.")

    result_direct = mks.trend_test(
        x=values,
        t=dates,
        ci_method='direct', # This is the default
        plot_path=direct_plot_file
    )

    # Convert slope and CI to annual for interpretation
    seconds_in_year = 365.25 * 24 * 60 * 60
    annual_slope_direct = result_direct.slope * seconds_in_year
    annual_lower_ci_direct = result_direct.lower_ci * seconds_in_year
    annual_upper_ci_direct = result_direct.upper_ci * seconds_in_year

    print("\nDirect CI Results:")
    print(f"Annual Slope: {annual_slope_direct:.4f}")
    print(f"Annual CI: ({annual_lower_ci_direct:.4f}, {annual_upper_ci_direct:.4f})")
    print(f"A plot has been saved to '{os.path.basename(direct_plot_file)}'.")
    print("-" * 60)

    # --- 4. Analysis with 'lwp' CI Method ---
    print("\n--- 4. Analysis with `ci_method='lwp'` ---")
    print("The 'lwp' method emulates the LWP-TRENDS R script. It uses linear")
    print("interpolation between the two slopes on either side of the calculated")
    print("rank. This can provide a more precise, non-integer estimate for the")
    print("confidence limits, but the difference is often small.")

    result_lwp = mks.trend_test(
        x=values,
        t=dates,
        ci_method='lwp',
        plot_path=lwp_plot_file
    )

    annual_slope_lwp = result_lwp.slope * seconds_in_year
    annual_lower_ci_lwp = result_lwp.lower_ci * seconds_in_year
    annual_upper_ci_lwp = result_lwp.upper_ci * seconds_in_year

    print("\nLWP CI Results:")
    print(f"Annual Slope: {annual_slope_lwp:.4f}")
    print(f"Annual CI: ({annual_lower_ci_lwp:.4f}, {annual_upper_ci_lwp:.4f})")
    print("\nConclusion: As shown, the Sen's slope is identical, but the confidence")
    print("intervals are slightly different due to the calculation method.")
    print(f"A plot has been saved to '{os.path.basename(lwp_plot_file)}'.")
    print("-" * 60)

# Restore stdout
sys.stdout = original_stdout
print(f"Example 13 script finished. Output saved to {output_file}")
