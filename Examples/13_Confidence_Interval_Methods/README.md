# Example 13: Comparing Confidence Interval Methods

This example compares the two methods available in `MannKenSen` for calculating the confidence intervals (CI) of the Sen's slope: `'direct'` (the default) and `'lwp'`.

## Key Concepts

The confidence intervals for the Sen's slope are determined by selecting two specific slopes from the sorted list of all pairwise slopes. The ranks of these two slopes (M_low and M_high) are calculated based on the variance of the S-statistic and the desired confidence level (alpha).

The two methods differ in how they use these ranks to find the final confidence limit values:

-   `ci_method='direct'` **(Default):** This method is simple and fast. It takes the calculated ranks (M_low and M_high), rounds them to the nearest integer, and uses these integers to directly index the sorted array of slopes. The confidence limits are actual slopes that were calculated between pairs of points in the dataset.

-   `ci_method='lwp'`: This method emulates the behavior of the LWP-TRENDS R script. It uses **linear interpolation** to estimate the confidence limits. For example, if a calculated rank is 25.7, this method will find the slope values at index 25 and 26 and calculate a new value that is 70% of the way between them. This can result in slightly different, more precise CI values that may not be actual slopes from the dataset.

The choice of method does **not** affect the Sen's slope itself, only the upper and lower bounds of its confidence interval.

## Script: `run_example.py`
The script generates a simple linear dataset with random noise. It then runs `trend_test` on this data twice:
1.  Once with the default `ci_method='direct'`.
2.  Once with `ci_method='lwp'`.

It prints the resulting annual slope and confidence intervals from both runs for a direct comparison and saves a plot for each.

## Results

### Direct CI Method Plot (`direct_ci_plot.png`)
![Direct CI Plot](direct_ci_plot.png)

### LWP CI Method Plot (`lwp_ci_plot.png`)
![LWP CI Plot](lwp_ci_plot.png)

### Output Analysis (`ci_methods_output.txt`)
By comparing the text output from the two runs, you will observe:
-   The **Annual Slope** is identical in both cases.
-   The **Annual CI** values are slightly different. The difference is usually very small, but the `'lwp'` method provides a non-integer, interpolated result.

**Conclusion:** The default `'direct'` method is generally sufficient and computationally efficient. The `'lwp'` method is provided for users who need to maintain consistency with the LWP-TRENDS R script or who require the slightly higher precision of an interpolated result.
