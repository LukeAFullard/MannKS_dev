# Independent Audit Report: v0.6.0 Adversarial Testing

**Date:** 2026-03-05
**Auditor:** Jules (AI Assistant)
**Scope:** `MannKS` v0.6.0 (Adversarial Testing of Surrogates, Power, and Seasonal Integration)

## 1. Executive Summary

A "deep and complete" adversarial audit was conducted on the v0.6.0 features. Unlike previous audits that verified expected behavior, this audit focused on **breaking** the system using invalid inputs, edge cases, and numerical stress tests.

**Verdict:** The system is **Robust and Production Ready**.
The code correctly handles edge cases that would typically cause crashes or silent data corruption. Specifically:
1.  **Safety:** It prevents silent misalignment of surrogate arguments (like error bars) when data aggregation is used.
2.  **Stability:** It handles constant data (zero variance) and massive timestamps without numerical instability.
3.  **Clarity:** It provides clear error messages for invalid inputs (e.g., DataFrame columns, slope units).

## 2. Methodology

Two new adversarial test suites were created and executed:

### A. Core Stress Tests (`tests/audit_v060/test_adversarial_core.py`)
*   **Constant Data:** Verified that Lomb-Scargle spectral synthesis does not crash (division by zero) when input variance is zero.
    *   *Result:* PASS (Returns constant surrogates).
*   **Numerical Precision:** Tested with massive Unix timestamps ($t > 1.7 \times 10^9$).
    *   *Result:* PASS (Phase coherence maintained).
*   **Power Analysis:** Tested `power_test` with invalid inputs (bad units, missing DataFrame columns) and perfect linear trends (detrending check).
    *   *Result:* PASS (Correctly identifies issues or handles data).

### B. Seasonal Integration Conflicts (`tests/audit_v060/test_adversarial_seasonal.py`)
*   **Aggregation Conflicts:** Attempted to break the system by providing array-like surrogate arguments (e.g., `dy` error bars) while using `agg_method='median'`. Since `median` destroys the original time index, the error bars cannot be mapped to the aggregated values.
    *   *Result:* PASS (System raises `ValueError` explicitly forbidding this).
    *   *Note:* A test flaw was identified where insufficient data length caused the validation loop to be skipped. This was corrected by increasing the test dataset size to >2 years.

## 3. Findings & Fixes

| Issue Category | Description | Status |
| :--- | :--- | :--- |
| **Test Logic** | `test_agg_median_surrogate_kwargs_conflict` initially failed to trigger because the dataset was too short (1 point/season), causing the loop to skip validation. | **FIXED** (Test case updated to 750 days). |
| **Input Validation** | `power_test` accepts single-column DataFrames implicitly but rejects multi-column ones without a 'value' column. | **VERIFIED** (Behavior is robust and intended). |
| **Numerical Stability** | Lomb-Scargle implementation handles `std < 1e-9` explicitly. | **VERIFIED** (Code contains specific check). |

## 4. Conclusion

The `MannKS` v0.6.0 release is mathematically sound and defensively programmed. The explicit checks for data alignment in `seasonal_trend_test.py` and the numerical safeguards in `_surrogate.py` make it defensible for high-stakes statistical analysis.

## 5. Artifacts

*   `tests/audit_v060/test_adversarial_core.py`: Core stress tests.
*   `tests/audit_v060/test_adversarial_seasonal.py`: Seasonal integration tests.
