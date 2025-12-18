import numpy as np
import MannKenSen as mks
import sys
import os

# Define the output directory
output_dir = 'Examples/14_Time_Vector_Nuances'
os.makedirs(output_dir, exist_ok=True)

# Define output file paths
output_file = os.path.join(output_dir, 'time_vector_output.txt')
# No plot is needed as the difference is purely numerical.

# Redirect output to a file
with open(output_file, 'w') as f:
    original_stdout = sys.stdout
    sys.stdout = f

    # --- 1. Introduction ---
    print("### Example 14: Time Vector Nuances (Numeric Data) ###")
    print("\nThis example highlights a crucial detail when working with numeric")
    print("time vectors (as opposed to datetimes): the units of the Sen's slope")
    print("are determined by the units of the time vector `t`.")
    print("\nUsing a simple integer sequence vs. a more meaningful time representation")
    print("(like fractional years) does NOT change the significance of the trend,")
    print("but it is critical for interpreting the slope's magnitude.")
    print("-" * 60)

    # --- 2. Generate Synthetic Data ---
    # Create a simple dataset representing 10 years of annual measurements.
    years = np.arange(2010, 2020)
    noise = np.random.normal(0, 0.5, len(years))
    trend = np.linspace(0, 5, len(years))
    values = 10 + trend + noise

    print("\n--- Generated Data ---")
    print("Generated 10 years of annual data with an increasing trend.")
    print("Years:", years)
    print("Values:", np.round(values, 2))
    print("-" * 60)

    # --- 3. Analysis with a Simple Integer Time Vector ---
    print("\n--- 3. Analysis with `t = [0, 1, 2, ...]` ---")
    print("First, we use a simple integer sequence as the time vector. This is")
    print("common but means the resulting slope is in 'units per index step'.")

    t_integer = np.arange(len(years))
    result_integer = mks.trend_test(x=values, t=t_integer)

    print("\nInteger Time Vector Results:")
    print(f"Slope: {result_integer.slope:.4f} (units per index)")
    print(f"P-value: {result_integer.p:.4f}")
    print(f"S-statistic: {result_integer.s}")
    print("\nThis slope is numerically correct, but not easily interpretable.")
    print("-" * 60)

    # --- 4. Analysis with a Fractional Year Time Vector ---
    print("\n--- 4. Analysis with `t = [2010, 2011, ...]` ---")
    print("Now, we use the actual years as the time vector. This makes the")
    print("resulting slope directly interpretable as 'units per year'.")

    t_years = years
    result_years = mks.trend_test(x=values, t=t_years)

    print("\nYear Time Vector Results:")
    print(f"Slope: {result_years.slope:.4f} (units per year)")
    print(f"P-value: {result_years.p:.4f}")
    print(f"S-statistic: {result_years.s}")
    print("\nThis slope has a clear, real-world meaning.")
    print("-" * 60)

    # --- 5. Conclusion ---
    print("\n--- 5. Conclusion ---")
    print("The P-value and S-statistic are IDENTICAL in both tests. The choice")
    print("of time vector does not affect the trend's significance, only the")
    print("magnitude and interpretability of the Sen's slope.")
    print("\nRecommendation: Always use a time vector with meaningful units")
    print("(e.g., years, fractional years) when possible.")
    print("-" * 60)


# Restore stdout
sys.stdout = original_stdout
print(f"Example 14 script finished. Output saved to {output_file}")
