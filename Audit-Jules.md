# MannKenSen Package Audit (Jules)

This document contains the findings of a deep, comprehensive audit of the `MannKenSen` package, conducted to ensure its reliability as a scientific tool.

## Audit Summary

| Priority | Issue | Module | Status |
|---|---|---|---|
| **High** | Numerically unstable handling of right-censored data. | `_stats.py` | **Identified** |
| **High** | Statistically unsound aggregation of censored data. | `seasonal_test`, `original_test` | **Identified** |
| **Medium** | Redundant tie correction in variance calculation. | `_stats.py` | **Identified** |
| **Medium** | Vague Sen's Slope warning for censored data. | `analysis_notes.py` | **Identified** |
| **Low** | Ambiguous rounding method for confidence interval indexing. | `_stats.py` | **Identified** |
| **Low** | Insufficient documentation for key parameters. | `README.md`, Docstrings | **Identified** |

## Detailed Findings

### Critical Priority
*(None identified at this time)*

### High Priority
- **Numerically Unstable Handling of Right-Censored Data (`_mk_score_and_var_censored`)**
  - **Issue:** The function modifies right-censored data by adding a small, arbitrary `tie_break_value`. This approach is numerically unstable and data-dependent.
  - **Recommendation:** Replace this arbitrary method with a more robust, non-parametric approach. A standard statistical technique is to treat right-censored values as having a rank greater than all observed values.

- **Statistically Unsound Aggregation of Censored Data (`seasonal_test`, `original_test`)**
  - **Issue:** The `agg_method='median'` and `'robust_median'` options are not statistically valid for censored data without more advanced methods (e.g., Kaplan-Meier estimation), which are not implemented.
  - **Recommendation:** Issue a `UserWarning` if aggregation is attempted on censored data and update documentation to strongly caution against this practice.

### Medium Priority
- **Redundant Tie Correction in Variance Calculation (`_mk_score_and_var_censored`)**
  - **Issue:** The function appears to apply two different forms of tie correction, which is redundant and likely incorrect.
  - **Recommendation:** Remove the initial, simpler tie correction and rely solely on the specialized correction terms designed for censored data.

- **Vague Sen's Slope Warning for Censored Data (`analysis_notes.py`)**
  - **Issue:** The warning "Sen slope influenced by left- and right-censored values" is ambiguous.
  - **Recommendation:** Refine the warning logic to be more specific, such as "Sen slope based on two censored values."

### Low Priority
- **Ambiguous Rounding for Confidence Interval Indexing (`_confidence_intervals`)**
  - **Issue:** The use of `np.round` for index calculation has platform-dependent behavior ("round half to even").
  - **Recommendation:** Document this behavior or replace it with a more explicit rounding method for better reproducibility.

- **Insufficient Documentation for Key Parameters (`README.md` and Docstrings)**
  - **Issue:** The scope and limitations of several key parameters (`lt_mult`, `gt_mult`, `time_method`, `agg_method`) are not documented with sufficient clarity.
  - **Recommendation:** Update all user-facing documentation to provide clear warnings and guidance on the appropriate use of these parameters.
