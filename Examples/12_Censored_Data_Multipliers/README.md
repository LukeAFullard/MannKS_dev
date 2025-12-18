# Example 12: The Impact of Censored Data Multipliers

This example explains the `lt_mult` and `gt_mult` parameters and demonstrates how they can be used for sensitivity analysis of the Sen's slope calculation.

## Key Concepts

The Mann-Kendall test (which determines the trend direction and significance) is a rank-based test. It only cares about the relative order of data points, not their magnitude. Therefore, the p-value, S-statistic, and z-score are **not affected** by the numeric substitutions for censored data.

However, the **Sen's slope** calculation, which determines the magnitude of the trend, requires numeric values for all data points. When data is censored, a substitution must be made. `MannKenSen` handles this with two parameters:

-   `lt_mult` (default `0.5`): The multiplier for left-censored data. For the slope calculation, a value like `'<10'` is replaced by `10 * lt_mult`.
-   `gt_mult` (default `1.0`): The multiplier for right-censored data. For the slope calculation, a value like `'>50'` is replaced by `50 * gt_mult`. The default is `1.0` following the USGS convention.

Changing these parameters allows the user to perform a sensitivity analysis. For example, if the calculated slope is not very sensitive to a wide range of multipliers (e.g., from 0.5 to 0.9), it increases confidence in the result.

## Script: `run_example.py`
The script generates a simple dataset with a clear increasing trend and several left-censored (`<`) data points. It then runs the `trend_test` twice:
1.  **With the default `lt_mult=0.5`**.
2.  **With a custom `lt_mult=0.75`**.

The script then prints the key results from both analyses to highlight the differences.

## Results

### Output Analysis (`multipliers_output.txt`)
The output file contains the results of the two analyses.

-   **P-value and S-statistic:** You will notice that these values are **identical** in both runs. This is the correct behavior, as the rank-based Mann-Kendall test is not influenced by the multiplier.

-   **Annual Slope:** The calculated Sen's slope is **different** in the two runs. The run with `lt_mult=0.75` produces a slightly higher slope because the numeric substitutions for the censored values were higher (e.g., `'<4'` was treated as `3.0` instead of `2.0`).

**Conclusion:** The `lt_mult` and `gt_mult` parameters are specialized tools for performing sensitivity analyses on the magnitude of the Sen's slope. They are a valuable feature for advanced users who need to understand the robustness of their trend estimates, but they do not alter the fundamental outcome of the Mann-Kendall significance test.
