# MannKenSen Package Audit

This document outlines a comprehensive audit of the `MannKenSen` Python package. The goal of this audit is to identify any potential issues in the codebase, statistical methodology, and overall structure to ensure its reliability as a scientific package.

## 1. Statistical Robustness

### 1.1 Censored Data Handling

- **`_mk_score_and_var_censored`**:
    - **Issue**: The function uses a tie-breaking method (`delx`, `dely`) that adds a small epsilon, calculated as `np.min(np.diff(unique_xx)) / 1000.0`. This approach is sensitive to the data's scale.
    - **Status**: **Resolved**
    - **Resolution**: The epsilon calculation was made more robust. It is now calculated as half the minimum difference between unique values (`min_diff / 2.0`) when a difference exists, or defaults to `1.0` if all values are identical.
- **`_sens_estimator_censored`**:
    - **Issue**: The default `method='lwp'` sets ambiguous slopes to 0. This is a statistically biased choice that can incorrectly suggest a "no trend" result.
    - **Status**: **Resolved**
    - **Resolution**: The default method was changed from `'lwp'` to `'nan'`, which is a more statistically neutral approach. The user-facing functions were also updated to use this new default.
- **`_aggregate_censored_median`**:
    - **Issue**: The logic for determining if a median is censored is a heuristic from the LWP-TRENDS R script and may not be universally robust.
    - **Status**: **Resolved**
    - **Resolution**: Added a note to the relevant docstrings to clarify that this is a heuristic intended to replicate the R script's behavior.

### 1.2 Code Clarity

- **`_stats.py`**:
  - **Issue:** The variance calculation in `_mk_score_and_var_censored` is a direct and complex translation from R and lacks explanatory comments.
  - **Status**: **Resolved**
  - **Resolution**: Added comments to the variance calculation section, explaining the statistical purpose of the `delc`, `deluc`, and `delu` correction terms, improving maintainability.

### 1.3 Confidence Intervals

- **`__confidence_intervals`**:
    - **Issue**: The function uses `np.interp` to find confidence intervals, which can be inaccurate for small or heavily tied datasets.
    - **Status**: **Resolved**
    - **Resolution**: The function was modified to use direct indexing of the sorted slopes array, which is a more statistically robust, non-parametric method.

## 2. Code Structure & Readability

- **`_utils.py`**:
    - **Issue**: This file was monolithic, containing over 500 lines of disparate functionality, making it hard to maintain.
    - **Status**: **Resolved**
    - **Resolution**: The `_utils.py` file was refactored into three smaller, more focused internal modules: `_stats.py`, `_helpers.py`, and `_datetime.py`.
- **Function Naming**:
    - **Issue**: Several internal functions used a double-underscore prefix, which is not standard for private module functions.
    - **Status**: **Resolved**
    - **Resolution**: All internal helper functions were renamed to use a single leading underscore.
- **Dead Code**:
    - **Issue**: The functions `__mk_score` and `__variance_s` were unused legacy code.
    - **Status**: **Resolved**
    - **Resolution**: The unused functions were removed from the codebase.

## 3. Error Handling & Validation

- **Input Validation**:
    - **Issue**: User-facing functions did not validate string-based enum parameters, leading to silent failures.
    - **Status**: **Resolved**
    - **Resolution**: Added explicit validation checks to `original_test` and `seasonal_test` that raise a `ValueError` for invalid parameter values.
- **`prepare_censored_data`**:
    - **Issue**: The error messages for malformed censored strings were not descriptive.
    - **Status**: **Resolved**
    - **Resolution**: Enhanced the error messages to be more informative (e.g., `ValueError: Invalid left-censored value format: '<'. Expected a number after the '<' symbol.`).
- **`seasonality_test`**:
    - **Issue**: The function would silently fail if a season had insufficient data, rather than continuing with the remaining seasons.
    - **Status**: **Resolved**
    - **Resolution**: The function now skips seasons with insufficient data, issues a `UserWarning`, and continues the analysis with the valid seasons.

## 4. Testing

- **Coverage Gaps**:
    - **Issue**: The test suite had gaps in coverage, particularly for `hicensor=True`, aggregation methods, and edge cases in data preparation.
    - **Status**: **Partially Resolved**
    - **Resolution**: The most critical gaps have been closed, and overall test coverage is high (93%). However, minor gaps for specific edge cases remain.
    - **Recommendation**: Write additional tests for the missed lines in `_helpers.py`, `plotting.py`, and `analysis_notes.py` to achieve 100% coverage.
- **Statistical Validation**:
    - **Issue**: There are no integration tests that validate the statistical output against a known, trusted implementation.
    - **Recommendation**: Create static test cases using data and results generated manually from the LWP-TRENDS R script to provide a baseline for correctness.

## 5. Documentation

- **Docstrings**:
    - **Issue**: User-facing docstrings referred to internal functions for implementation details.
    - **Status**: **Resolved**
    - **Resolution**: The docstrings for public functions were updated to be self-contained and comprehensive.
- **`README.md`**:
    - **Issue**: The `README.md` had several inaccuracies and omissions, including an incorrect default value for `sens_slope_method`, a missing parameter, and a broken link.
    - **Status**: **Resolved**
    - **Resolution**: The `README.md` has been updated to be consistent with the current codebase. The incorrect default value was corrected, the missing parameter was added, and the broken link was removed and replaced with an explanatory note.
- **`prepare_censored_data` Docstring**:
  - **Issue:** The docstring did not specify the function's behavior for `np.nan` inputs.
  - **Status**: **Resolved**
  - **Resolution**: The docstring was updated to clarify that `np.nan` values are treated as non-censored numeric values.
