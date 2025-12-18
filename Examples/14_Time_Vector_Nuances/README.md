
# Example 14: Time Vector Nuances (Numeric Data)

This example highlights that for numeric time vectors, the units of the Sen's slope are determined by the units of the time vector `t`.

## Key Concepts
The Mann-Kendall test for significance (p, s, z) is rank-based and is **not** affected by the scale of the time vector. However, the Sen's slope calculation is `(y2 - y1) / (t2 - t1)`, so its units depend directly on the units of `t`.

-   If `t = [0, 1, 2, ...]`, the slope is in **units per index step**.
-   If `t = [2010, 2011, ...]` the slope is in **units per year**.

## Script: `run_example.py`
The script analyzes the same data twice: once with a simple integer time vector and once with a vector of years.

## Results
The p-value and S-statistic are identical, but the slope's magnitude is different and more interpretable when using a meaningful time vector.

### Analysis with `t = [0, 1, 2, ...]`
- **Slope:** 0.5480 (units per index)\n- **P-value:** 0.0003\n- **S-statistic:** 41.0\n

### Analysis with `t = [2010, 2011, ...]`
- **Slope:** 0.5480 (units per year)\n- **P-value:** 0.0003\n- **S-statistic:** 41.0\n

**Conclusion:** Always use a time vector with meaningful units (e.g., years) when possible to ensure the Sen's slope is directly interpretable.
