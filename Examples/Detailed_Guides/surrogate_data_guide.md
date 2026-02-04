# A Guide to Surrogate Data Testing

The `surrogate_test` functionality in `MannKS` (introduced in v0.6.0) provides a robust way to test for trends in the presence of **serial correlation** (also known as autocorrelation or "Red Noise").

## The Problem: Red Noise

Standard statistical tests, including the Mann-Kendall test, assume that the "noise" (residuals) in your time series is independent (White Noise). However, real-world environmental, financial, and physical data often exhibit **persistence**:
*   A high value is likely to be followed by another high value.
*   A low value is likely to be followed by another low value.

This property is called **Red Noise** (or AR(1) processes). To a standard trend test, this persistence can look exactly like a deterministic trend, leading to a high rate of **Type I Errors** (False Positives). You might conclude a trend exists when the data is simply wandering randomly.

## The Solution: Surrogate Data

Instead of relying on theoretical distributions that assume independence, we use a computational approach:

1.  **Generate Surrogates:** We create thousands of synthetic datasets ("surrogates") that mimic the statistical properties of your original data:
    *   Same probability distribution (values).
    *   Same power spectrum (autocorrelation structure).
    *   **BUT** randomized phases, destroying any deterministic trend.
2.  **Compare:** We calculate the Mann-Kendall trend statistic (S or Tau) for your original data and for all the surrogates.
3.  **Test:** If your observed trend is stronger than, say, 95% of the trends found in the random surrogates, we reject the null hypothesis.

## Available Methods

`MannKS` offers two advanced methods for generating surrogates, automatically selected based on your data structure.

### 1. IAAFT (Iterated Amplitude Adjusted Fourier Transform)
*   **Best for:** Evenly spaced data.
*   **How it works:** It iteratively adjusts the phases of the Fourier transform to match the original power spectrum while replacing the amplitudes to match the original value distribution.
*   **Strengths:** Preserves both linear correlations and the exact marginal distribution of the data.

### 2. Lomb-Scargle Spectral Synthesis
*   **Best for:** Unevenly spaced data (missing values, irregular sampling).
*   **How it works:** Uses the Lomb-Scargle periodogram (via `astropy`) to estimate the power spectrum of irregular data. It then generates random noise with this spectrum and samples it at the exact observation times of your original data.
*   **Strengths:** Does not require interpolation (which introduces bias).

## Parameters

You can access surrogate testing directly through the `trend_test` function.

### `surrogate_method`
-   **Type:** `str`, **Default:** `'none'`
-   **Options:**
    *   `'none'`: Standard Mann-Kendall test (no surrogate testing).
    *   `'auto'`: Automatically chooses `'iaaft'` for evenly spaced data and `'lomb_scargle'` for unevenly spaced data. **(Recommended)**.
    *   `'iaaft'`: Force IAAFT method.
    *   `'lomb_scargle'`: Force Lomb-Scargle method.

### `n_surrogates`
-   **Type:** `int`, **Default:** `1000`
-   **Description:** The number of synthetic datasets to generate.
-   **Advice:** Higher numbers (e.g., 2000 or 10000) give more precise p-values but take longer to compute. 1000 is usually sufficient for a standard significance level of 0.05.

### `surrogate_kwargs`
-   **Type:** `dict`, **Default:** `None`
-   **Description:** Advanced configuration for the generation algorithms.
-   **Common Options:**
    *   `{'freq_method': 'log'}` (for Lomb-Scargle): Uses logarithmically spaced frequencies, which can be better for capturing power laws in red noise.
    *   `{'dy': errors}` (for Lomb-Scargle): If your data has measurement uncertainties, you can pass them here.

## Interpreting the Output

When `surrogate_method` is used, the `trend_test` result will contain a `surrogate_result` field.

```python
result = trend_test(x, t, surrogate_method='auto')
sr = result.surrogate_result
```

### Key Fields

*   **`sr.p_value`**: The proportion of surrogates that had a trend statistic as strong as or stronger than your original data.
    *   **p < 0.05**: Significant. Your trend is likely real, not just red noise.
    *   **p > 0.05**: Not significant. Your "trend" is indistinguishable from random red noise.
*   **`sr.trend_significant`**: Boolean (`True`/`False`) indicating if the null hypothesis was rejected at the given alpha.
*   **`sr.method`**: The method actually used (`'iaaft'` or `'lomb_scargle'`).
*   **`sr.notes`**: Warnings or information about the process (e.g., if data was aggregated).

## Example Workflow

```python
from MannKS import trend_test

# 1. Run the test
result = trend_test(
    data, times,
    surrogate_method='auto',
    n_surrogates=1000
)

# 2. Check standard MK result (assuming independence)
print(f"Standard MK p-value: {result.p:.4f}")

# 3. Check Surrogate result (robust to red noise)
sr = result.surrogate_result
print(f"Surrogate p-value: {sr.p_value:.4f}")

if sr.trend_significant:
    print("Confirmed: Trend is significant even against red noise.")
else:
    print("Caution: Trend may be an artifact of serial correlation.")
```
