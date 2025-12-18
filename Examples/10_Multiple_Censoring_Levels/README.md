# Example 10: Handling Data with Multiple Censoring Levels

This example demonstrates the robustness of the `MannKenSen` package in handling complex, real-world datasets that contain a mixture of numerous, different censoring levels.

## Key Concepts

Real-world environmental data often comes from various sources or from labs whose methods change over time. This can result in a dataset with many different detection limits, such as `<1`, `<2`, `<5`, and even right-censored data like `>50` if an instrument has an upper limit.

The statistical engine of `MannKenSen` is designed to handle this complexity automatically. When comparing any two data points, it correctly interprets their relationship based on their numerical values and censoring codes. For example:
-   `<2` vs. `2.1` is a clear increase (+1).
-   `<2` vs. `1.9` is ambiguous (0), as the `<2` value could be higher or lower than `1.9`.
-   `<2` vs. `<5` is also ambiguous (0), as their true values could overlap.
-   `<2` vs. `>10` is a clear increase (+1), as the highest possible value for `<2` is less than the lowest possible value for `>10`.

The user does not need to perform any special handling for this. The standard workflow of `prepare_censored_data` followed by `trend_test` is sufficient.

## Script: `run_example.py`
The script generates a synthetic dataset with a clear increasing trend over 20 years. The data is intentionally complex, containing:
-   Uncensored numeric values.
-   Multiple levels of left-censored data (`<1`, `<2`, `<5`).
-   Multiple levels of right-censored data (`>10`, `>15`).

The script then runs the standard analysis workflow and generates a single plot and output file.

## Results

### Analysis Plot
-   **`multi_censor_plot.png`**:
    ![Multi-Censor Plot](multi_censor_plot.png)

The plot effectively visualizes the complex data. Left-censored data points are shown as triangles pointing down, while right-censored data points are triangles pointing up, clearly distinguishing them from the uncensored circular data points.

### Output Analysis (`multi_censor_output.txt`)

The text output shows that the `trend_test` function successfully processes the data and correctly identifies the "Highly Likely Increasing" trend, providing a valid Sen's slope and confidence intervals. The `prop_censored` field in the output also confirms that the package recognized a significant portion of the data as censored.

**Conclusion:** `MannKenSen` is a robust tool capable of handling complex, messy, real-world censored data without requiring any special configuration from the user beyond the standard preprocessing step.
