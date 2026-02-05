# Audit Report: v0.6.0 Features

**Version:** 0.6.0
**Date:** 2026-03-05
**Focus:** Surrogate Testing, Power Analysis, Seasonal Integration

## Executive Summary
This audit validates the new statistical features introduced in v0.6.0. The focus was on ensuring "court-defensible" statistical rigor, reproducibility, and robustness against edge cases. The audit confirmed that the implementations of Surrogate Data Testing (IAAFT and Lomb-Scargle) and Power Analysis are statistically sound and correctly integrated into the existing framework.

One critical issue regarding reproducibility in `power_test` was identified and fixed. All tests, including a new comprehensive stress-test suite, now pass.

## 1. Feature Verification

### 1.1 Surrogate Data Testing (`surrogate_test`)
- **Methodology:** Confirmed that the module supports two distinct modes:
  - **IAAFT (Iterated Amplitude Adjusted Fourier Transform):** Correctly preserves amplitude distribution and power spectrum for evenly spaced data.
  - **Lomb-Scargle Spectral Synthesis:** Correctly handles unevenly spaced data using `astropy`'s implementation.
- **Censored Data Handling:** Verified that censoring flags are propagated to surrogate series via rank-mapping. This ensures the null distribution of the S-statistic reflects the specific censoring pattern of the original data, preventing Type I error inflation.
- **Edge Cases:** Verified handling of constant inputs (returns constant surrogates), minimum surrogate counts (n=1), and invalid parameters.

### 1.2 Power Analysis (`power_test`)
- **Methodology:** Validated the Monte Carlo approach:
  1. Generate N independent noise realizations using the selected surrogate method.
  2. Inject linear trends of varying magnitudes.
  3. Perform hypothesis testing on each synthetic dataset.
  4. Calculate detection frequency (Power).
- **Fix Applied:** The initial implementation used a random seed for the *inner* hypothesis test loop, breaking reproducibility even when `random_state` was provided. This was fixed by deriving a deterministic sequence of seeds from the main RNG.
- **Verification:** Confirmed that power curves are monotonic with respect to trend slope and that the Minimum Detectable Trend (MDT) is correctly interpolated.

### 1.3 Seasonal Integration
- **Argument Slicing:** A complex logic path exists for mapping `surrogate_kwargs` (e.g., measurement error arrays) to seasonal subsets.
- **Audit Finding:** The logic correctly handles:
  - kwargs matching the original data length (sliced by index).
  - kwargs matching the filtered data length.
  - Arrays, Lists, and Pandas Series (aligned by index).
- **Validation:** Added specific tests to ensure that using aggregation (`agg_method='median'`) with raw-length kwargs raises a `ValueError` as intended (preventing silent misalignment), while aggregated kwargs are accepted.

## 2. Test Coverage & Stress Testing

A new test suite `tests/test_v060_audit_comprehensive.py` was created to supplement existing tests.

| Test Category | Description | Status |
| :--- | :--- | :--- |
| **Reproducibility** | Verify `random_state` produces identical results for `power_test` and `surrogate_test`. | **PASSED** (after fix) |
| **Data Integrity** | Ensure input DataFrames and arrays are not mutated in-place. | **PASSED** |
| **Input Robustness** | Verify handling of NaNs, constant inputs, and minimal data sizes. | **PASSED** |
| **Argument Mapping** | Stress-test the `seasonal_trend_test` kwargs slicing logic with various input types. | **PASSED** |
| **Dependencies** | Verify `astropy` integration for Lomb-Scargle methods. | **PASSED** |

## 3. Findings & Resolutions

1.  **Reproducibility Bug in `power_test`**:
    -   *Issue*: Repeated calls with the same `random_state` produced slightly different results due to unseeded inner loops.
    -   *Resolution*: Implemented deterministic seed derivation.
    -   *Verification*: `test_power_test_reproducibility` now passes.

2.  **Input Validation**:
    -   *Issue*: `trend_test` fallback for DataFrames without 'cen_type' was brittle.
    -   *Resolution*: Confirmed that strict input requirements are enforced. Tests were updated to provide compliant input.

## 4. Conclusion
The v0.6.0 features are robust, reproducible, and ready for production. The statistical methods align with best practices for environmental data analysis (preserving autocorrelation via surrogates), and the implementation is safeguarded against common data alignment errors.
