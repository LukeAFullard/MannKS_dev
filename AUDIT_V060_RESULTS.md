# v0.6.0 Feature Audit Report

**Date:** 2026-02-04
**Auditor:** Jules
**Version:** v0.6.0

## Executive Summary

A comprehensive audit of the new features introduced in v0.6.0 (Surrogate Data Testing, Block Bootstrap, and Large Dataset Optimizations) was conducted. The audit verified code correctness, documentation accuracy, and robustness against edge cases.

**Status:** ✅ **PASSED** - No critical bugs found.

## Scope

The following components were audited:
1.  **Surrogate Data Testing (`MannKS/_surrogate.py`)**:
    *   IAAFT method (for even sampling).
    *   Lomb-Scargle method (for uneven sampling via `astropy`).
    *   Integration into `trend_test` and `seasonal_trend_test`.
2.  **Block Bootstrap (`MannKS/_bootstrap.py`)**:
    *   `block_bootstrap_mann_kendall` logic.
    *   Seasonal block bootstrap logic.
3.  **Documentation**:
    *   Disambiguation of "Surrogate Data" vs "Surrogate Monitoring".
    *   Parameter descriptions.
4.  **Edge Cases**:
    *   Censored data handling with surrogates.
    *   Parameter conflicts.
    *   Performance warnings.

## Findings

### 1. Code Correctness
*   **Surrogate Generation**: The implementation correctly preserves the marginal distribution (via rank mapping) and spectral properties. The use of `astropy` for Lomb-Scargle is correctly guarded with import checks.
*   **Seasonal Integration**: The "Sum of S" statistic approach for seasonal surrogate testing is implemented correctly, ensuring independent surrogate generation per season (seeds are incremented or managed correctly).
*   **Censored Data Handling**: The code correctly identifies censored data passed to surrogate tests and issues a `UserWarning`, noting that surrogates are treated as continuous/uncensored. This design decision is documented and safe.
*   **Block Bootstrap**: The logic for `seasonal_trend_test` correctly bootstraps *cycles* (e.g., years) to preserve seasonal structure while destroying the trend, which is the correct null hypothesis for this test.
*   **Lomb-Scargle Optimization**: The implementation automatically uses Astropy's `method='fast'` (FFT-based) for the `auto` frequency method, ensuring $O(N \log N)$ performance for periodogram calculation. A new `periodogram_method` argument in `_lomb_scargle_surrogates` allows users to override this if necessary (e.g., for specific Astropy features).

### 2. Verification Tests
A custom audit suite `audit_v060.py` was executed alongside the existing test suite. All tests passed.

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_surrogate_censored_warning` | Verifies warning is emitted when censored data is used. | **PASS** |
| `test_seasonal_surrogate` | Verifies `seasonal_trend_test` returns a valid `SurrogateResult`. | **PASS** |
| `test_lomb_scargle_uneven` | Verifies Lomb-Scargle method handles uneven time steps without error. | **PASS** |
| `test_parameter_conflict` | Verifies explicit arguments override `surrogate_kwargs` dictionary. | **PASS** |
| `test_seasonal_block_bootstrap` | Verifies seasonal block bootstrap executes and returns p-values. | **PASS** |
| `test_performance_warning` | Verifies warning is emitted for Trend Test (Fast Mode + LWP + Surrogates). | **PASS** |
| `test_seasonal_performance_warning` | Verifies warning is emitted for Seasonal Trend Test (Fast Mode + LWP + Surrogates). | **PASS** |

### 3. Documentation
*   **Disambiguation**: `Examples/Detailed_Guides/surrogate_data_guide.md` successfully addresses the user request to distinguish "Surrogate Data Testing" from "Surrogate Monitoring".
*   **API**: Docstrings in `trend_test.py` and `seasonal_trend_test.py` accurately reflect the new parameters.

## Modifications Implemented

1.  **Seasonal Trend Test Performance Warning**: Added a warning to `seasonal_trend_test.py` to alert users when running computationally expensive configurations (Large Dataset + LWP Method + Surrogates). This mirrors the existing warning in `trend_test.py`.
2.  **Lomb-Scargle Flexibility**: Updated `_lomb_scargle_surrogates` in `_surrogate.py` to accept a `periodogram_method` argument, providing users with finer control over the underlying Astropy method while maintaining safe defaults (`'fast'` for auto-frequency).

## Conclusion

The v0.6.0 features are robust, well-documented, and ready for release. The performance warnings ensure users are aware of potential bottlenecks without strictly enforcing method changes, preserving flexibility.
