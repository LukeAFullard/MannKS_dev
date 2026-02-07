# Independent Audit Report: v0.6.0 Features

**Date:** 2026-03-05
**Auditor:** Jules (AI Assistant)
**Scope:** `MannKS` v0.6.0 (Surrogate Testing, Power Analysis, Seasonal Integration)

## 1. Executive Summary

An independent, adversarial audit was conducted on the new features introduced in version 0.6.0. The audit focused on "correctness, edge cases, and trust ability," bypassing existing tests to verify the system from first principles.

**Conclusion:** The v0.6.0 features are **production-ready**. A critical edge case involving datetime handling in `surrogate_test` was identified and fixed, along with a cosmetic warning bug. The system now robustly handles all tested inputs, including direct datetime array injection.

## 2. Methodology

Two test suites (`tests/audit_v060/test_independent_audit.py` and `tests/audit_v060/test_v060_regression_fixes.py`) were used to test the system under stress. Key areas tested included:

1.  **Lomb-Scargle Stability:** Verified that the spectral synthesis method handles degenerate cases (constant data, massive numerical offsets) without crashing or producing invalid results (NaNs).
2.  **Surrogate Argument Integrity:** Verified that `trend_test` and `seasonal_trend_test` raise explicit `ValueError`s when a user attempts to pass array-like arguments (e.g., `dy` error bars) while also aggregating data (e.g., daily to monthly). This ensures that data and error bars never silently become misaligned.
3.  **Power Analysis Correctness:**
    *   **Slope Scaling:** confirmed that `slope_scaling` parameters ('year', 'second') correctly transform input trends.
    *   **Reproducibility:** Confirmed that `power_test` produces bit-exact identical results when the same `random_state` is provided.
    *   **Input Handling:** Verified robust handling of censored DataFrames.
4.  **Adversarial Inputs:** Tested response to invalid methods, zero surrogates, and mismatched array lengths.

## 3. Findings

| Test Case | Result | Notes |
| :--- | :--- | :--- |
| **Lomb-Scargle Constant Data** | ✅ PASS | Returns constant surrogates (variance preserved as 0). |
| **Lomb-Scargle Extreme Offset** | ✅ PASS | Precision maintained for values +1e9. |
| **Agg/Surrogate Conflict** | ✅ PASS | Raises `ValueError` as expected to prevent misalignment. |
| **Power Slope Scaling** | ✅ PASS | Large trends detected, negligible trends (when scaled) ignored. |
| **Power Reproducibility** | ✅ PASS | Identical results with fixed seed. |
| **Input Validation** | ✅ PASS | Correctly rejects invalid `agg_period` and missing columns. |
| **Surrogate Time Handling** | ✅ FIXED | `surrogate_test` crashed with datetime inputs due to NumPy 2.x type strictness. Fixed by enforcing numeric conversion. |
| **Warning Formatting** | ✅ FIXED | Corrected loop variable naming in IAAFT warnings. |

## 4. Recommendations

*   **Retain Audit Suite:** The `test_independent_audit.py` file should be kept in the repository as a regression safeguard.
*   **Documentation:** The strict requirement for `agg_period` (e.g., using 'month' instead of 'M' when checking for conflicts) should be noted in developer guides, although standard usage remains flexible.

## 5. Artifacts

*   `tests/audit_v060/test_independent_audit.py`: The independent test suite.
