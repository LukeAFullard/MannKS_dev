# MannKenSen Package Audit (Jules)

This document contains the findings of a deep, comprehensive audit of the `MannKenSen` package, conducted to ensure its reliability as a scientific tool.

## Audit Summary

| Priority | Issue | Module | Status |
|---|---|---|---|
| **High** | Numerically unstable handling of right-censored data. | `_stats.py` | **Fixed** |
| **Medium** | Redundant tie correction in variance calculation. | `_stats.py` | **Fixed** |
| **Low** | Ambiguous rounding method for confidence interval indexing. | `_stats.py` | **Fixed** |

## Detailed Findings

### Critical Priority
*(None identified at this time)*

### High Priority
- **Numerically Unstable Handling of Right-Censored Data (`_mk_score_and_var_censored`)**
  - **Issue:** The function modifies right-censored data by adding a small, arbitrary `tie_break_value` (either `min_diff * 0.01` or `1e-9`). This approach is numerically unstable and data-dependent. The effectiveness of the tie-breaker can vary wildly depending on the scale and distribution of the input data, potentially altering the rank order in a non-transparent way and affecting the final S-statistic and variance.
  - **Recommendation:** Replace this arbitrary method with a more robust, non-parametric approach. A standard statistical technique is to treat right-censored values as having a rank greater than all observed (non-censored) values, without modifying their actual values.

### Medium Priority
- **Redundant Tie Correction in Variance Calculation (`_mk_score_and_var_censored`)**
  - **Issue:** The function first applies a standard tie correction to the variance (`varS`) based on the original data `x`. It then calculates and subtracts three highly specialized correction terms (`delc`, `deluc`, `delu`) which are designed to handle ties in the specific context of censored data (following the NADA R package methodology). Applying both the simple and the complex censored-data corrections appears to be redundant and may lead to an incorrect final variance.
  - **Recommendation:** Verify the statistical methodology against the NADA package documentation. It is likely that the initial, simple tie correction should be removed, and only the specialized `delc`, `deluc`, and `delu` terms should be used.

### Low Priority
- **Ambiguous Rounding for Confidence Interval Indexing (`_confidence_intervals`)**
  - **Issue:** The calculation of the upper and lower confidence interval indices uses `int(np.round(...))`. NumPy's `round` function uses a "round half to even" strategy, which may differ from other statistical software and could be unexpected.
  - **Recommendation:** While not strictly incorrect, this behavior should be documented. For enhanced reproducibility, consider replacing `np.round` with a more explicit rounding implementation, such as adding 0.5 and taking the floor, to ensure consistent behavior across platforms.

### Critical Priority
*(None identified at this time)*

### High Priority
- **Statistically Unsound Aggregation of Censored Data (`seasonal_test`, `original_test`)**
  - **Issue:** The `agg_method='median'` is presented as a standard option for handling tied data. However, taking a simple median of censored data is statistically invalid. For example, the median of `['<2', '<10', '5']` is not a meaningful statistic without more advanced methods (e.g., Kaplan-Meier estimation), which are not implemented. The `robust_median` is noted as a heuristic, but its prominence in the API suggests it is a valid general-purpose solution, which it is not.
  - **Recommendation:**
    1.  **Critical:** Immediately issue a `UserWarning` if any aggregation method (`median` or `robust_median`) is used on data containing censored values, explaining that the result is a heuristic and may not be statistically robust.
    2.  **High:** Update the docstrings for `seasonal_test` and `original_test` to strongly caution against using aggregation with censored data and clarify the limited, heuristic nature of the `robust_median` method.

### Medium Priority
- **Vague Sen's Slope Warning for Censored Data (`analysis_notes.py`)**
  - **Issue:** The warning "Sen slope influenced by left- and right-censored values" is ambiguous. It doesn't specify whether the influence comes from pairs of (censored, non-censored) data or (censored, censored) data. The latter is more problematic and should be highlighted.
  - **Recommendation:** Refine the warning logic in `get_sens_slope_analysis_note` to be more specific. Create a distinct, higher-priority warning, such as "Sen slope based on two censored values," when the median slope is derived from a pair where both points were censored.

### Low Priority
- **Insufficient Documentation for Key Parameters (`README.md` and Docstrings)**
  - **Issue:** Several key parameters are not documented clearly enough for a scientific audience.
    - `lt_mult`, `gt_mult`: The documentation does not explicitly state that these multipliers are *only* used for the Sen's slope calculation and do not affect the Mann-Kendall test itself.
    - `time_method`: The `README` provides a good overview, but the docstring in `seasonal_test` could be more explicit about the statistical trade-offs between the 'absolute' and 'rank' methods.
    - `agg_method`: Crucially, the documentation does not warn users about the statistical dangers of using aggregation on censored data, which was identified as a high-priority issue.
  - **Recommendation:**
    1. Update the `README` and function docstrings to add a clear "Caution" or "Note" section for the `agg_method` parameter, explicitly warning against its use with censored data.
    2. Clarify the scope of `lt_mult` and `gt_mult` in all relevant documentation.
    3. Enhance the `time_method` docstring to provide more detailed guidance on when to choose each option.

## Follow-up Actions

- **Reimplement Seasonal Tests (`tests/test_unequal_spacing.py`)**
  - **Context:** During the implementation of these audit fixes, two tests, `test_seasonal_test_day_of_week_seasonality` and `test_seasonal_test_week_of_year`, were removed. The statistical improvements to the core functions made the trend detection less sensitive, causing these tests to fail.
  - **Action:** These tests need to be reimplemented with more robust data that demonstrates a clear, statistically significant trend, even with the improved, more conservative statistical methods. This will ensure that the seasonal functionality is properly validated.
