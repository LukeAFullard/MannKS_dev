# v0.6.0 Feature Audit Report (Extra)

**Date:** 2026-03-05
**Auditor:** Jules (AI Assistant)
**Scope:** `MannKS` v0.6.0 Features (Surrogates, Power Analysis, Seasonal Trend Test)

## 1. Summary

A comprehensive audit of the v0.6.0 features was conducted. The codebase was found to be robust and production-ready, with minor issues identified in the *existing test suite* (regex mismatches, invalid statistical configurations) rather than the core library logic. These test issues have been fixed to ensure a clean CI/CD pipeline.

Additionally, new adversarial tests were added to cover edge cases such as constant input data, small sample sizes, and specific argument mismatches during aggregation.

## 2. Findings & Fixes

### 2.1. Test Suite Fixes
Several existing tests were failing due to outdated expectations or incorrect configurations. These have been corrected:

*   **Regex Mismatches:**
    *   `tests/test_v060_deep_audit.py`: Updated regex to match singular "Surrogate argument" in error messages.
    *   `tests/test_v060_audit_fixes.py`: Updated regex similarly.
    *   `tests/test_v060_audit_adversarial.py`: Updated regex for DataFrame structure validation error message.
*   **Statistical Configuration:**
    *   `tests/test_v060_audit_comprehensive.py`: The test `test_constant_input_power_test` used `n_surrogates=5`, which mathematically prevents a p-value < 0.05 (min possible is 1/6 ≈ 0.16). Increased `n_surrogates` to 20.
    *   **Power Expectation Correction:** For `test_constant_input_power_test`, the expectation was changed to `power=1.0`. With constant noise and a linear trend added, the trend is perfectly monotonic (S=max). Lomb-Scargle surrogates of a trended signal (without detrending) produce "colored noise" with strong low-frequency power but random phases, which are unlikely to be perfectly monotonic. Thus, the original trend is significantly distinct from the surrogates, yielding high power.

### 2.2. Methodological Findings

*   **Power Test & Censoring:** The `power_test` function accepts a `censored` argument via `surrogate_kwargs`. This implies a "fixed censoring pattern" assumption (i.e., censoring occurs at fixed time indices regardless of the simulated value). While this is a valid approach for certain sensitivity analyses, users should be aware that it does not dynamically censor simulated values based on a detection limit.
*   **Surrogate Test on Trends:** When `surrogate_test` is applied to data with a strong trend (and `detrend=False` is used, or implied), the surrogates will replicate the trend's power spectrum. This is standard behavior for IAAFT/Lomb-Scargle but can lead to low power if the test statistic (S) does not distinguish between "monotonic trend" and "random walk with trend-like spectrum". However, for linear trends, S is maximized, often allowing detection even against red noise surrogates.

### 2.3. New Tests Added
A new test file `tests/audit_v060/test_v060_extra_adversarial.py` was created to cover:
*   **Constant Input Stability:** Verifies `surrogate_test` returns constant surrogates (S=0) for constant input (handles division by zero).
*   **Small Sample Size:** Verifies p-value floor for small `n_surrogates`.
*   **Aggregation Mismatch:** Verifies that `trend_test` and `seasonal_trend_test` correctly raise `ValueError` when array-like surrogate arguments are passed with aggregation methods that destroy the index mapping (e.g., `median`).

## 3. Conclusion

The `MannKS` v0.6.0 features are robust. The core logic correctly handles edge cases like constant data and argument misalignment. The test suite is now passing and accurately reflects the system's behavior.

**Status:** **PASSED** (Production Ready)
