# v0.6.0 Audit Report

## Executive Summary
The v0.6.0 features ("Surrogate Data Testing" and "Block Bootstrap") are functional but contain several implementation inconsistencies and omissions that limit their robustness, particularly for advanced configurations (censored data, robust tie-breaking) and seasonal analysis.

## Findings

### 1. Block Bootstrap (Autocorrelation Handling)
*   **Issue:** `trend_test` fails to propagate the `tie_break_method` parameter to the block bootstrap logic.
    *   **Impact:** Even if a user requests `tie_break_method='robust'`, the bootstrap hypothesis test uses the default `'lwp'` method for its internal Mann-Kendall calculations. This leads to inconsistency between the main test statistic and the bootstrap distribution.
    *   **Contrast:** `seasonal_trend_test` correctly implements this propagation in its inline bootstrap logic.

### 2. Surrogate Data Testing
*   **Issue 1: Parameter Omission:** `surrogate_test` ignores critical Mann-Kendall configuration parameters (`mk_test_method`, `tie_break_method`, `tau_method`).
    *   **Impact:** The surrogate hypothesis test always runs with default settings, potentially comparing a "Robust MK" score (from the main test) against "Standard MK" scores (from surrogates), invalidating the p-value.
*   **Issue 2: Censored Data Support:** `surrogate_test` strictly treats all input data as uncensored.
    *   **Impact:** Censoring flags are stripped before surrogate generation. For datasets with significant censoring (e.g., many values below detection limit), the surrogate test essentially tests a different hypothesis (values vs. noise) than the main test (ranks of censored data vs. noise), which is methodologically flawed.
*   **Issue 3: Seasonal Support:** Surrogate testing is **not implemented** for `seasonal_trend_test`, despite the plan implying broader availability.
*   **Issue 4: Performance:** For large datasets (N > 5,000) using `fast` mode, `surrogate_test` does not utilize the optimization strategies (stochastic Sen's slope, etc.) and instead runs the full $O(N \log N)$ or $O(N^2)$ test for every surrogate.
    *   **Impact:** A standard test taking ~3s might take ~3000s (50 mins) if 1000 surrogates are requested.

## Recommendations
1.  **Patch `trend_test.py`:** Update the call to `block_bootstrap_mann_kendall` to pass `tie_break_method` and `mk_test_method`.
2.  **Patch `_bootstrap.py`:** Update `block_bootstrap_mann_kendall` signature to accept and use these parameters.
3.  **Update `surrogate_test`:**
    *   Accept and use MK configuration parameters.
    *   Implement basic handling for censored data (or explicitly raise a warning/error that it is unsupported).
    *   Integrate with "Fast Mode" logic if possible, or emit a stronger performance warning.

## Verification
A reproduction script (`verify_audit.py`) was created and executed, confirming the parameter propagation failures and the lack of censoring support in the surrogate module.
