
# Example 12: The Impact of Censored Data Multipliers

This example explains the `lt_mult` and `gt_mult` parameters, which are used for sensitivity analysis of the Sen's slope calculation with censored data.

## Key Concepts
The Sen's slope calculation requires numeric values. For censored data, a substitution is made:
-   `lt_mult` (default `0.5`): A value like `'<10'` is replaced by `10 * lt_mult`.
-   `gt_mult` (default `1.0`): A value like `'>50'` is replaced by `50 * gt_mult`.

Changing these parameters **does not** affect the Mann-Kendall significance test (p-value, S-statistic), which is rank-based. It only affects the slope's magnitude.

## Script: `run_example.py`
The script analyzes a simple censored dataset twice: once with the default `lt_mult=0.5` and once with `lt_mult=0.75`.

## Results
The p-value and S-statistic are identical in both runs, as expected. The slope may or may not change depending on the data's structure.

### Default Multiplier (`lt_mult=0.5`)
- **Annual Slope:** 1.0000\n- **P-value:** 0.0009\n- **S-statistic:** 37.0\n

### Custom Multiplier (`lt_mult=0.75`)
- **Annual Slope:** 1.0000\n- **P-value:** 0.0009\n- **S-statistic:** 37.0\n

**Conclusion:** The `lt_mult` and `gt_mult` parameters are specialized tools for sensitivity analysis of the Sen's slope magnitude, without altering the trend's significance.
