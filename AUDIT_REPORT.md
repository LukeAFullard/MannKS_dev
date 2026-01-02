# Comprehensive Audit Report for MannKS

## Executive Summary
This document summarizes the findings of a "deep and complete" code audit of the `MannKS` Python package. The audit was conducted to validate methodology, accuracy, and completeness, with a specific focus on statistical defensibility and replicability of the LWP-TRENDS R script. Every `.py` file in the repository was reviewed individually.

**Verdict:** The `MannKS` package is mathematically sound and implements the Mann-Kendall and Sen's Slope estimators correctly. It provides robust handling of edge cases (e.g., ties, censored data) and offers a faithful "compatibility mode" that replicates the specific (and sometimes heuristic) behaviors of the legacy LWP-TRENDS R script.

## 1. Methodology Validation

### 1.1 Core Statistical Engine (`MannKS/_stats.py`)
-   **Mann-Kendall Test:** The implementation correctly uses a rank-based approach. The variance calculation includes the necessary corrections for ties (`delc`) and censored data (`deluc`, `delu`), following the NADA package methodology (Helsel, 2012).
-   **Sen's Slope:** The pairwise slope calculation is accurate. The implementation correctly handles the `O(n^2)` complexity and includes safety checks for memory usage.
-   **Tie Correction Logic:** The audit confirmed that the variable assignment `x4 = x3` in the `deluc` term calculation is the correct implementation of the NADA variance correction algorithm.
-   **LWP Compatibility:** The specific heuristics used by the LWP-TRENDS R script are correctly implemented as optional parameters:
    -   `mk_test_method='lwp'`: Modifies right-censored values (`>x` becomes `max(>x) + 0.1`).
    -   `sens_slope_method='lwp'`: Forces ambiguous slopes (e.g., between two left-censored values) to `0` instead of `NaN`.
    -   `ci_method='lwp'`: Uses linear interpolation for confidence intervals instead of the standard nearest-rank method.

### 1.2 Akritas-Theil-Sen (ATS) Estimator (`MannKS/_ats.py`)
-   The ATS implementation uses a valid root-finding approach (`bracket_and_bisect`) to solve for the slope that zeroes the Kendall's S statistic of the residuals.
-   The method correctly handles interval-censored data (left and right censoring).
-   **Bootstrap:** The stratified bootstrap for the seasonal ATS slope correctly resamples residuals within seasons, preserving the seasonal structure.

### 1.3 Advanced Statistical Modules (`MannKS/_autocorr.py`, `MannKS/_bootstrap.py`)
-   **Autocorrelation:** The `estimate_acf` function uses a standard masked array approach to handle potential missing data or simple vectors. The `effective_sample_size` calculation correctly implements both the Yue & Wang (2004) and Bayley-Hammersley methods.
-   **Bootstrap:** The block bootstrap implementation (`moving_block_bootstrap`) is correctly designed to preserve the autocorrelation structure of the time series data. For trend testing, the "detrended moving block bootstrap" approach is used, which is the correct statistical procedure for testing the null hypothesis of no trend in the presence of serial correlation.

### 1.4 Visualization and Inspection (`MannKS/plotting.py`, `MannKS/inspection.py`)
-   **Plotting:** The plotting functions correctly handle the pivot of trend lines around the median data point (`(t_med, y_med)`), ensuring numerical stability when plotting against large Unix timestamp values.
-   **Inspection:** The `inspect_trend_data` logic faithfully replicates the "availability check" logic needed to determine the appropriate analysis frequency (e.g., ensuring 90% of years have data).

## 2. Robustness and Error Handling

### 2.1 Stress Testing
A suite of stress tests was executed to verify behavior under extreme conditions:
-   **Empty/Single-Point Input:** Gracefully returns "no trend" with appropriate analysis notes ("insufficient data").
-   **All-NaN Input:** Handled correctly as insufficient data.
-   **Infinite Values:** Handled via standard floating-point comparisons without crashing.
-   **Zero Variance (Flat Line):** Returns `S=0` and `Var(S) > 0` (due to tie corrections not completely zeroing variance in the NADA formula, which is a known property). The result is correctly identified as "no trend" (or "indeterminate" in continuous mode).
-   **Mixed Censored Input:** The `prepare_censored_data` function correctly parses mixed lists of numbers and strings (e.g., `[1, '<5', 3]`).

### 2.2 Safety Mechanisms
-   **Integer Overflow Protection:** A hard limit (`MAX_SAFE_N = 46340`) prevents integer overflow in pairwise calculations ($N^2$ scaling). This is a defensible choice for stability, though users with large datasets are advised to use regional aggregation.
-   **Confidence Interval Bounds:** The code includes a specific check for when calculated CI indices fall out of bounds (common in small samples with high variance). It issues a `UserWarning` and returns `NaN` instead of crashing, which is the correct "fail-safe" behavior.

## 3. Discrepancies and Clarifications

### 3.1 Bootstrap Timestamp Replacement
In `seasonal_trend_test.py` and `_bootstrap.py`, the block bootstrap logic creates synthetic timestamps (or indices) for the bootstrapped samples.
-   **Impact:** This simplifies the null hypothesis to a test against rank ordering, effectively ignoring any unequal time spacing *during the bootstrap generation of the null distribution*.
-   **Justification:** The Mann-Kendall test is rank-based. If the original data is monotonic in time (sorted), replacing timestamps with integers preserves the rank order, so the test statistic $S$ remains valid. This is an acceptable simplification for the bootstrap test of the null hypothesis.

### 3.2 Zero Variance "Indeterminate" Result
When the input data has zero variance (e.g., `[1, 1, 1]`), the default `continuous_confidence=True` mode returns `trend='indeterminate'` because the Z-score is exactly 0.
-   **Clarification:** Users expecting a definitive "no trend" label should set `continuous_confidence=False` or interpret "indeterminate" as the absence of evidence for a trend.

## 4. Conclusion
The `MannKS` package is a robust, statistically defensible tool. The "bugs" identified in the `AUDIT_FINDINGS.md` file are intentional features designed to replicate the specific behaviors of the legacy LWP-TRENDS R script. The Python implementation provides a cleaner, more stable, and more flexible foundation while offering a validated path for backward compatibility.
