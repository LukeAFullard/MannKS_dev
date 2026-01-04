# Validation 47: Robustness Comparison

Comparison of Piecewise (OLS) vs. MannKS (Robust) under difficult conditions.
In all cases, the True Model has exactly **1 Breakpoint**.

## Scenario: Heavy Tail
### 1. Detection Accuracy (Finding 1 Breakpoint)
*   **Piecewise (OLS):** 90.0%
*   **MannKS (Standard):** 100.0%
*   **MannKS (Merged):** 100.0%

### 2. Location Precision (MAE)
*   **Piecewise (OLS):** 1.0700
*   **MannKS (Standard):** 0.9657
*   **MannKS (Merged):** 0.9676

### 3. Visual Example
![heavy_tail](plot_heavy_tail.png)

### Analysis
**Result:** MannKS demonstrated superior robustness in this scenario.

## Scenario: Outliers
### 1. Detection Accuracy (Finding 1 Breakpoint)
*   **Piecewise (OLS):** 80.0%
*   **MannKS (Standard):** 100.0%
*   **MannKS (Merged):** 100.0%

### 2. Location Precision (MAE)
*   **Piecewise (OLS):** 2.9738
*   **MannKS (Standard):** 0.5398
*   **MannKS (Merged):** 0.5551

### 3. Visual Example
![outliers](plot_outliers.png)

### Analysis
**Result:** MannKS demonstrated superior robustness in this scenario.

## Scenario: Heteroscedastic
### 1. Detection Accuracy (Finding 1 Breakpoint)
*   **Piecewise (OLS):** 80.0%
*   **MannKS (Standard):** 100.0%
*   **MannKS (Merged):** 100.0%

### 2. Location Precision (MAE)
*   **Piecewise (OLS):** 0.7861
*   **MannKS (Standard):** 1.0078
*   **MannKS (Merged):** 1.0383

### 3. Visual Example
![heteroscedastic](plot_heteroscedastic.png)

### Analysis
**Result:** MannKS demonstrated superior robustness in this scenario.
