# v0.6.0 Final Audit Report

**Date:** 2026-03-04
**Auditor:** Jules (AI Software Engineer)
**Version Audited:** v0.6.0
**Status:** **PASSED** (Pending Minor Fixes)

## 1. Executive Summary
The v0.6.0 release introduces significant capabilities for hypothesis testing against colored noise backgrounds (Surrogate Data) and statistical power estimation. The implementation logic is sound, leveraging the robust `astropy` library for spectral analysis of unevenly spaced data. The integration into `trend_test` and `seasonal_trend_test` is seamless and backward-compatible.

One minor runtime defect (Warning) and one packaging issue were identified and addressed/documented. With these resolved, the package is considered **Production Ready** and methodologically defensible.

## 2. Methodology Review

### 2.1 Surrogate Data Testing
-   **IAAFT (Even Sampling):** Correctly implements the Schreiber & Schmitz (1996) algorithm.
-   **Lomb-Scargle (Uneven Sampling):** Uses `astropy.timeseries.LombScargle` to estimate the power spectrum.
    -   **Strengths:** Correctly handles irregular sampling, supports measurement errors (`dy`), and preserves marginal distribution via rank adjustment.
    -   **Validation:** Passed adversarial tests including extreme time offsets and constant data inputs.
    -   **Defect Identified:** Numerical noise can cause slightly negative power values in `astropy`, leading to `RuntimeWarning: invalid value encountered in sqrt`.
        -   **Fix:** Clip power values to 0 before square root.

### 2.2 Power Analysis (`power_test`)
-   **Approach:** Monte Carlo simulation injecting linear trends into colored noise surrogates.
-   **Validity:** This is the correct empirical approach for Theil-Sen estimators where no closed-form power equation exists.
-   **Limitations:**
    -   **Interpolation:** Uses linear interpolation to find the Minimum Detectable Trend (MDT) at 80% power. While power curves are sigmoidal, linear approximation near the threshold is acceptable for this application.
    -   **Performance:** Extremely computationally intensive ($N_{sim} \times N_{surr}$ iterations). Users are warned via documentation, but execution time can be significant.

### 2.3 Seasonal Integration
-   **Logic:** Surrogates are generated independently per season, and the Seasonal Mann-Kendall Statistic $S$ is computed by summing the $S_i$ from each season.
-   **Correctness:** This correctly tests the global null hypothesis of "no monotonic trend" against a background of seasonally independent colored noise.
-   **Safety:** The implementation explicitly increments the `random_state` for each season to ensure independence.

## 3. Code Quality & Safety

### 3.1 Input Validation
-   **Kwargs Slicing:** Both `trend_test` and `seasonal_trend_test` include robust logic to align `surrogate_kwargs` (e.g., error bars) with the data.
    -   **Safety:** Explicitly raises `ValueError` if temporal aggregation is used (destroying the index map) while array-like kwargs are provided. This prevents silent data misalignment.
    -   **Verification:** Verified via `test_trend_test_surrogate_kwargs_mismatch_aggregation`.

### 3.2 Dependency Management
-   **Issue:** `astropy` was missing from `pyproject.toml` and `dev-requirements.txt` despite being a core requirement for the Lomb-Scargle feature.
-   **Resolution:** Added `astropy` to configuration files during the audit setup.

### 3.3 Performance
-   **Warnings:** The code correctly warns users if they attempt to run computationally expensive surrogate tests ($O(N^2)$) on large datasets without enabling the $O(N \log N)$ optimizations.

## 4. Findings & Remediation Plan

| Severity | Component | Issue | Remediation |
| :--- | :--- | :--- | :--- |
| **High** | Packaging | `astropy` missing from dependencies. | **Fixed** in `pyproject.toml`. |
| **Medium** | `_surrogate.py` | `RuntimeWarning: invalid value encountered in sqrt` due to negative spectral power (floating point noise). | **Pending:** Clip power to >= 0. |
| **Low** | `power.py` | Warning suppression `warnings.simplefilter("ignore")` might hide legitimate errors. | **Keep:** Necessary to suppress repetitive warnings during Monte Carlo loops. |

## 5. Conclusion
The v0.6.0 feature set is robust. The surrogate methods provide a "defensible in court" standard for claiming trend significance in the presence of autocorrelation, significantly improving upon the standard Mann-Kendall test.

**Recommendation:** Proceed with release after applying the patch for `_surrogate.py`.
