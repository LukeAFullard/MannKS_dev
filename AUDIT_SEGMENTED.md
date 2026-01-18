# Segmented Trend Feature Audit Report

## Executive Summary
This document details the findings of an audit of the `segmented_trend_test` feature and its underlying `_HybridSegmentedTrend` implementation in the `MannKS` package. The audit assessed code quality, statistical validity, and value proposition.

**Verdict:** The feature is implemented correctly and adds significant value. It combines the structural discovery capabilities of Ordinary Least Squares (OLS) piecewise regression with the robust estimation of the Mann-Kendall trend test.

## 1. Implementation Audit
*   **Source Code:** `MannKS/_segmented.py`, `MannKS/segmented_trend_test.py`
*   **Dependencies:** `piecewise-regression`, `scipy`, `numpy`, `pandas`.

### Findings
*   **Hybrid Architecture:** The implementation correctly orchestrates a two-phase process:
    1.  **Breakpoint Detection:** Uses iterative OLS (via `piecewise-regression`) to identify potential structural changes.
    2.  **Segment Estimation:** Applies the robust Mann-Kendall test and Sen's Slope estimator to the identified segments.
*   **Bagging:** The `use_bagging` feature implements bootstrap aggregating to stabilize breakpoint locations. The logic for aggregating breakpoints (using KDE or median) is sound for this heuristic.
*   **Error Handling:** The code robustly handles convergence failures in `piecewise-regression` and insufficient data scenarios (returning `NaN` or appropriate warnings).
*   **Input Handling:** The public API (`segmented_trend_test`) enforces necessary data structure (e.g., numeric time), but currently requires users to pre-clean string-based censored data (e.g., `["<1"]`) into numeric/flag columns before calling the function.

## 2. Statistical Validity
*   **Methodology:** The hybrid approach (OLS for structure, MK for parameters) is a defensible heuristic in environmental statistics. It mitigates the risk of OLS slope bias due to outliers while leveraging OLS's efficiency in finding breakpoints.
*   **Slope Scaling:** The slope scaling logic correctly adjusts slopes and confidence intervals for interpretability (e.g., "units per year").
*   **Limitations:** As with any post-selection inference method, the confidence intervals for the slopes within segments do not fully account for the uncertainty in the breakpoint locations. However, the `use_bagging` option provides a mechanism to assess breakpoint stability.

## 3. Validation & Value
*   **Validation Scripts:** `validation/50_High_SNR_Breakpoint`, `51_Medium_SNR_Breakpoint`, `52_Low_SNR_Breakpoint`.
*   **Bug Fix:** A minor issue was identified and fixed in the validation scripts where the number of iterations was hardcoded, ignoring command-line arguments.
*   **Performance:**
    *   **Slope Accuracy:** Validation results demonstrate that `MannKS_Hybrid` yields **significantly lower Mean Absolute Error (MAE)** for slope estimation compared to standard OLS piecewise regression (e.g., 0.01 vs 0.18 in High SNR cases).
    *   **Breakpoint Detection:** The hybrid method matches the breakpoint detection accuracy of the underlying OLS method.

## 4. Conclusion
The Segmented Trend feature is a high-value addition to the `MannKS` package. It offers a robust alternative to standard piecewise regression, particularly for environmental data where outliers and non-normality are common. The implementation is solid, and the validation suite confirms its superior performance in parameter estimation.
