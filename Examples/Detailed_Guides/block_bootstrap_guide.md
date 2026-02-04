# A Guide to Block Bootstrap for Autocorrelated Data

Standard Mann-Kendall tests and Sen's slope calculations rely on the assumption that observations are independent. However, real-world time series often exhibit **autocorrelation** (or serial correlation), where each value is correlated with previous values. This violates the independence assumption and can lead to **Type I Errors** (detecting a trend when none exists) or inaccurate confidence intervals.

`MannKS` addresses this using the **Moving Block Bootstrap** (MBB) method, which preserves the autocorrelation structure of the data during resampling.

## When to Use It

You should consider using Block Bootstrap if:
*   Your data has significant serial correlation (e.g., environmental data with "memory").
*   You see "Autocorrelation detected" in the `analysis_notes` of your output.
*   You want the most robust p-values and confidence intervals possible for dependent data.

## How It Works

The library uses a sophisticated dual-approach to bootstrapping to ensure correctness for both hypothesis testing and estimation:

### 1. For P-values: Detrended Residual Block Bootstrap
To correctly test the Null Hypothesis ($H_0$: No Trend), we must first remove any existing trend from the data while keeping the noise structure intact.
1.  **Detrend:** We calculate an initial Sen's slope and subtract the trend from the data to get the *residuals*.
2.  **Block Resample:** We resample these residuals in blocks (e.g., chunks of 5 consecutive points). This preserves the short-term correlation within each block.
3.  **Test:** We calculate the Mann-Kendall statistic ($S$) for thousands of these synthetic "no-trend" datasets.
4.  **Compare:** The p-value is the proportion of synthetic $S$ values that are more extreme than your observed $S$.

### 2. For Confidence Intervals: Pairs Block Bootstrap
To estimate the uncertainty of the slope (Confidence Interval), we need to preserve the relationship between Time ($t$) and Value ($x$).
1.  **Block Resample Pairs:** We resample blocks of $(t, x)$ pairs together.
2.  **Sort:** The resampled pairs are sorted by time (as bootstrap shuffling disturbs the order).
3.  **Estimate Slope:** We calculate the Sen's slope for each resampled dataset.
4.  **Intervals:** The 95% Confidence Interval is derived directly from the 2.5th and 97.5th percentiles of the bootstrap slope distribution.

## Parameters

You can control this behavior using the following parameters in `trend_test` (and `seasonal_trend_test`).

### `autocorr_method`
-   **Type:** `str`, **Default:** `'none'`
-   **Options:**
    *   `'none'`: Standard calculations (assumes independence).
    *   `'auto'`: Automatically calculates the Lag-1 Autocorrelation (ACF1). If ACF1 > 0.1 (statistically significant), it automatically switches to `'block_bootstrap'`. **(Recommended)**.
    *   `'block_bootstrap'`: Forces the use of the bootstrap method regardless of the ACF value.
    *   `'yue_wang'`: Uses an alternative variance correction method (effective sample size). Faster, but relies on asymptotic assumptions.

### `block_size`
-   **Type:** `int` or `'auto'`, **Default:** `'auto'`
-   **Description:** The size of the blocks used for resampling.
-   **Details:**
    *   `'auto'`: The function calculates the autocorrelation function (ACF) of the residuals and selects a block size equal to the correlation length (where ACF drops below 0.1). This is adaptive to your specific data structure.
    *   `int`: You can manually specify a block size (e.g., `block_size=12` for monthly data with annual dependence).

### `n_bootstrap`
-   **Type:** `int`, **Default:** `1000`
-   **Description:** The number of bootstrap resamples to generate.
-   **Advice:**
    *   `1000`: Good balance of speed and precision for standard p-values (p ~ 0.001 resolution).
    *   `10000`: Recommended for publication-quality results or if you need to detect very small p-values.

## Example Usage

```python
from MannKS import trend_test

# 1. Automatic Detection (Recommended)
# If autocorrelation is found, it will switch to bootstrap automatically.
result = trend_test(x, t, autocorr_method='auto')

# 2. Forced Bootstrap with Custom Settings
result = trend_test(
    x, t,
    autocorr_method='block_bootstrap',
    block_size=5,       # Resample in blocks of 5 observations
    n_bootstrap=2000    # Use 2000 iterations for higher precision
)

# Check the output metadata
print(f"Correction Applied: {result.block_size_used is not None}")
print(f"Block Size: {result.block_size_used}")
print(f"P-value: {result.p:.4f}")
```

## Interpreting the Results

When block bootstrapping is used:
*   **P-value:** Represents the probability of observing the trend under the null hypothesis of *autocorrelated* noise. It is typically larger (less significant) than the standard p-value because autocorrelation reduces the effective sample size.
*   **Confidence Intervals:** Will typically be wider than standard intervals, correctly reflecting the increased uncertainty due to the data "memory".
*   **Metadata:** The result object will contain `block_size_used`, indicating the calculated or specified block size.
