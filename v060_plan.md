# v0.6.0 Development Plan: Surrogate Data Methods

This document outlines the plan for introducing surrogate data methods to the `MannKS` package in version 0.6.0. The primary goal is to enhance the robustness of trend significance testing, particularly for time series with complex autocorrelation structures (Red Noise) and irregular sampling.

## Rationale

The standard Mann-Kendall test assumes independent residuals (white noise). In many environmental and financial applications, data exhibits serial correlation (persistence), which can inflate Type I errors (false positives). While the existing `block_bootstrap` method addresses variance estimation (Confidence Intervals), it does not explicitly test the hypothesis: *"Is this trend distinguishable from a stochastic process with the same power spectrum?"*

Surrogate data methods generate synthetic datasets that preserve the statistical properties (autocorrelation, amplitude distribution) of the original series but destroy any deterministic trend. By comparing the Mann-Kendall S statistic of the original data against the distribution of S statistics from the surrogates, we can perform a rigorous hypothesis test.

## Status: Implemented

The following core features have been implemented as of 2026-03-04:

*   [x] **IAAFT Surrogates:** Implemented `_iaaft_surrogates` for evenly spaced data using `numpy.fft`.
*   [x] **Lomb-Scargle Surrogates:** Implemented `_lomb_scargle_surrogates` using `astropy.timeseries.LombScargle`.
    *   Supports unevenly spaced data (irregular sampling).
    *   Handles floating means (Generalized Lomb-Scargle) for trend robustness.
    *   Supports measurement uncertainties (`dy`) for weighted analysis.
    *   Includes spectral synthesis via direct summation (with chunking for memory safety).
    *   Includes rank adjustment to preserve the marginal distribution of the input.
*   [x] **Integration:** `trend_test` now accepts `surrogate_method`, `n_surrogates`, and `surrogate_kwargs`.
*   [x] **Testing:** Comprehensive tests added in `tests/test_surrogate.py` covering null cases, trend cases, and parameter integration.

## Proposed Features (Completed)

We have added a `surrogate_test` function and integrated it into the main `trend_test` workflow.

### 1. `surrogate_test` Function

A new standalone function to generate surrogates and compute significance. It leverages `astropy` for robust spectral analysis.

```python
def surrogate_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    dy: Optional[np.ndarray] = None,
    method: str = 'auto',
    n_surrogates: int = 1000,
    random_state: Optional[int] = None,
    # Advanced Astropy Parameters (Sensible defaults provided)
    freq_method: str = 'auto',
    normalization: str = 'standard',
    fit_mean: bool = True,
    center_data: bool = True,
    **kwargs
) -> SurrogateResult:
    """
    Performs a trend significance test using surrogate data.
    ...
    """
```

### 2. Algorithms

#### A. Lomb-Scargle Surrogates (For Uneven Sampling)
*   **Engine:** `astropy.timeseries.LombScargle`.
*   **Methodology:**
    1.  Compute the Generalized Lomb-Scargle periodogram (PSD) of the detrended data. This handles floating means and measurement uncertainties (`dy`) correctly.
    2.  Generate random phases $\phi \sim U[0, 2\pi)$.
    3.  Reconstruct the surrogate time series $x_{surr}(t)$ at the **original** irregular time points $t_i$ using the spectral components:
        $$ x_{surr}(t_i) = \sum_{k} \sqrt{P(f_k)} \cos(2\pi f_k t_i + \phi_k) $$
    4.  (Optional) Rank-adjust to preserve the original amplitude distribution (similar to IAAFT).
*   **Pros:**
    *   Mathematically rigorous for uneven data.
    *   Handles floating mean (trend-robust).
    *   Fast $O(N \log N)$ implementation via Astropy.
    *   Supports measurement uncertainties.

#### B. IAAFT (For Even Sampling)
*   **Methodology:** Iteratively adjusts the Fourier phases and amplitudes to match both the power spectrum and the value distribution of the original data.
*   **Pros:** Preserves both linear correlation and marginal distribution. Fast ($O(N \log N)$ via FFT).
*   **Cons:** Assumes even sampling.

## Validation Strategy

To ensure the scientific validity of the surrogate methods, we employ the following verification steps (implemented in `tests/test_surrogate.py`):

1.  **Null Case (Red Noise, No Trend):**
    *   **Scenario:** Generate 100 points of AR(1) red noise (correlated random walk) with *no* underlying linear trend.
    *   **Expectation:** The `surrogate_test` should return a high p-value (> 0.05), correctly identifying that any apparent trend is consistent with the background noise process.
    *   **Result:** Verified. The test correctly fails to reject the null hypothesis.

2.  **Trend Case (Red Noise + Trend):**
    *   **Scenario:** Add a deterministic linear trend to the AR(1) noise.
    *   **Expectation:** The `surrogate_test` should return a low p-value (< 0.05), correctly distinguishing the added trend from the noise.
    *   **Result:** Verified. The test correctly rejects the null hypothesis.

3.  **Irregular Sampling Verification:**
    *   **Scenario:** Use an unevenly spaced time vector (`t` with random gaps).
    *   **Expectation:** The `surrogate_test` with `method='lomb_scargle'` should run without error and correctly identify trends, whereas `method='iaaft'` would warn about potential bias.
    *   **Result:** Verified.

4.  **Automatic Method Selection:**
    *   **Scenario:** Pass evenly and unevenly spaced data with `method='auto'`.
    *   **Expectation:** The system correctly selects 'iaaft' for even data and 'lomb_scargle' for uneven data (if `astropy` is present).
    *   **Result:** Verified.

## User Examples & Education

The following examples illustrate how to use the new functionality in practice.

### Example 1: Basic Usage with `trend_test`

By default, `trend_test` runs the standard Mann-Kendall test. You can enable surrogate testing by setting `surrogate_method='auto'`.

```python
import numpy as np
from MannKS import trend_test

# Generate synthetic red noise with a trend
t = np.arange(100)
noise = np.random.randn(100)
trend = 0.05 * t
x = trend + noise # Correlated noise simulation

# Run standard test + surrogate test
result = trend_test(x, t, surrogate_method='auto', n_surrogates=500)

print(f"Standard MK Trend: {result.trend}")
print(f"Standard p-value: {result.p:.4f}")

# Access surrogate results
if result.surrogate_result:
    sr = result.surrogate_result
    print(f"Surrogate p-value: {sr.p_value:.4f}")
    print(f"Is trend significant against red noise? {sr.trend_significant}")
```

### Example 2: Uneven Sampling with Lomb-Scargle

For irregular data (e.g., missing observations), `MannKS` automatically uses Lomb-Scargle spectral synthesis if `astropy` is installed.

```python
# Uneven time vector
t_uneven = np.sort(np.random.uniform(0, 100, 50))
x_uneven = 0.1 * t_uneven + np.random.randn(50)

result = trend_test(x_uneven, t_uneven, surrogate_method='auto')

print(f"Method used: {result.surrogate_result.method}") # 'lomb_scargle'
```

### Example 3: Advanced Usage (Uncertainties & Configuration)

Power users can pass specific parameters to the underlying Astropy Lomb-Scargle engine using `surrogate_kwargs`.

```python
# Data with measurement errors
dy = np.ones_like(x_uneven) * 0.5  # Constant error of 0.5

result = trend_test(
    x_uneven,
    t_uneven,
    surrogate_method='lomb_scargle',
    n_surrogates=1000,
    surrogate_kwargs={
        'dy': dy,                   # Weighted periodogram
        'normalization': 'psd',     # Normalize by PSD
        'freq_method': 'log'        # Use logarithmic frequency spacing
    }
)
```
