import numpy as np
import MannKenSen as mks

# --- 1. Generate Synthetic Data ---
# This example demonstrates the simplest use case: a non-seasonal trend test
# on a dataset with a simple numeric time vector.
np.random.seed(42)
n_samples = 50
time = np.arange(n_samples)

# Create data with a clear upward trend (slope of approx. 0.1) and add noise
trend = 0.1 * time
noise = np.random.normal(0, 0.5, n_samples)
values = trend + noise

# --- 2. Perform the Trend Test ---
# Call the trend_test function with the data.
# Since the data is not censored, we don't need to pre-process it.
result = mks.trend_test(x=values, t=time)

# --- 3. Generate README ---
# The results are formatted into a string to be embedded in the README.
result_summary = f"""
- **Trend Classification:** {result.classification}
- **Is Trend Significant? (h):** {result.h}
- **P-value (p):** {result.p:.4f}
- **Sen's Slope:** {result.slope:.4f}
- **Mann-Kendall Score (s):** {result.s}
- **Kendall's Tau:** {result.Tau:.4f}
"""

readme_content = f"""
# Example 2: Basic Non-Seasonal Trend Test (Numeric Time)

This example demonstrates the simplest use case of the `MannKenSen` package: performing a non-seasonal trend test on a dataset with a simple numeric time vector.

## Script: `run_example.py`
The script performs the following actions:
1.  Generates a synthetic dataset with 50 data points, a clear upward trend, and a simple integer time vector (`t = [0, 1, 2, ...]`).
2.  Calls the `mks.trend_test` function to perform the analysis.
3.  Captures the key results and dynamically generates this `README.md` file, embedding the results below.

## Results
The `trend_test` function returns a `namedtuple` containing the full results of the analysis. The most critical fields for interpretation are listed below.

{result_summary}

### Interpretation
-   The **p-value** is very low (well below 0.05), and `h` is `True`, indicating a statistically significant trend.
-   The **Sen's Slope** is positive, confirming the trend is increasing. The value (`~0.1`) is the calculated rate of change, which is consistent with the trend we added to the synthetic data.
-   The **Classification** of "Highly Likely Increasing" provides a clear, human-readable summary of the result.

**Conclusion:** This basic example shows the fundamental workflow for performing a trend test on simple numeric data.
"""

with open('Examples/02_Basic_Non_Seasonal_Numeric/README.md', 'w') as f:
    f.write(readme_content)

print("Successfully generated README for Example 2.")
