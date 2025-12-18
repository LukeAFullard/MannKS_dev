# Example 14: Time Vector Nuances (Numeric Data)

This example highlights a crucial concept for users working with numeric (i.e., non-datetime) time vectors: the units of the Sen's slope are directly inherited from the units of the time vector `t` provided to the `trend_test` function.

## Key Concepts

The Mann-Kendall test for significance (calculating `p`, `s`, `z`) is a **rank-based test**. This means it only considers the relative order of the data points, not their numeric spacing. As a result, the significance of a trend will be identical whether your time vector `t` is `[0, 1, 2, 3]` or `[1980, 1990, 2000, 2010]`.

However, the **Sen's slope** calculation is different. It is calculated as the median of all pairwise slopes, where each slope is `(y2 - y1) / (t2 - t1)`. The denominator `(t2 - t1)` means that the units of the resulting slope are `[units of x] / [units of t]`.

This has a major impact on the interpretability of your results:
-   If `t` is a simple integer sequence `[0, 1, 2, ...]`, the slope is in **units per index step**.
-   If `t` is a list of years `[2010, 2011, 2012, ...]`, the slope is in **units per year**.
-   If `t` is fractional days, the slope is in **units per day**.

## Script: `run_example.py`
The script generates a simple dataset representing 10 years of annual measurements with a clear increasing trend. It then runs the `trend_test` twice on the exact same `values`:
1.  **With a simple integer time vector:** `t = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`
2.  **With a year-based time vector:** `t = [2010, 2011, 2012, ..., 2019]`

The script then prints the key results from both analyses to highlight the differences and similarities.

## Results

### Output Analysis (`time_vector_output.txt`)

The text output file is the key result for this example. When you inspect it, you will find:

-   **P-value and S-statistic:** These values are **identical** for both runs. This correctly demonstrates that the statistical significance of the trend is independent of the time vector's units.

-   **Slope:** The calculated Sen's slope is **different** in the two runs. The slope from the integer-based time vector is much larger because the time step is always 1. The slope from the year-based time vector is smaller and is directly interpretable as the rate of change per year.

**Conclusion:** For the most interpretable results, always provide a time vector `t` that has meaningful, real-world units. While it doesn't change the statistical outcome of the Mann-Kendall test, it is essential for correctly understanding the magnitude of the trend from the Sen's slope.
