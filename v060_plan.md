# v0.6.0 Development Plan: Surrogate Data Methods

This document outlines the plan for introducing surrogate data methods to the `MannKS` package in version 0.6.0. The primary goal is to enhance the robustness of trend significance testing, particularly for time series with complex autocorrelation structures (Red Noise) and irregular sampling.

## Rationale

The standard Mann-Kendall test assumes independent residuals (white noise). In many environmental and financial applications, data exhibits serial correlation (persistence), which can inflate Type I errors (false positives). While the existing `block_bootstrap` method addresses variance estimation (Confidence Intervals), it does not explicitly test the hypothesis: *"Is this trend distinguishable from a stochastic process with the same power spectrum?"*

Surrogate data methods generate synthetic datasets that preserve the statistical properties (autocorrelation, amplitude distribution) of the original series but destroy any deterministic trend. By comparing the Mann-Kendall S statistic of the original data against the distribution of S statistics from the surrogates, we can perform a rigorous hypothesis test.

## Proposed Features

We propose adding a `surrogate_test` function and integrating it into the main `trend_test` workflow.

### 1. `surrogate_test` Function

A new standalone function to generate surrogates and compute significance.

```python
def surrogate_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    method: str = 'auto',
    n_surrogates: int = 1000,
    random_state: Optional[int] = None,
    **kwargs
) -> SurrogateResult:
    """
    Performs a trend significance test using surrogate data.

    Parameters
    ----------
    method : str
        'auto': Selects based on sampling regularity.
        'iaaft': Iterated Amplitude Adjusted Fourier Transform (for even sampling).
        'lomb_scargle': Spectral synthesis using Lomb-Scargle periodogram (for uneven sampling).
        'car1': Parametric Continuous AutoRegressive (1) model (faster for simple red noise).
    n_surrogates : int
        Number of surrogate series to generate.
    ...
    """
```

### 2. Algorithms

#### A. Lomb-Scargle Surrogates (For Uneven Sampling)
*   **Methodology:**
    1.  Compute the Lomb-Scargle periodogram (PSD) of the detrended data.
    2.  Generate random phases $\phi \sim U[0, 2\pi)$.
    3.  Reconstruct the time series at the **original** irregular time points $t_i$ using the spectral components:
        $$ x_{surr}(t_i) = \sum_{k} \sqrt{P(f_k)} \cos(2\pi f_k t_i + \phi_k) $$
    4.  (Optional) Rank-adjust to preserve the original amplitude distribution (similar to IAAFT).
*   **Pros:** Mathematically rigorous for uneven data; no interpolation artifacts.
*   **Cons:** Computationally expensive ($O(N^2)$ or $O(N \cdot N_{freq})$). Requires optimization (e.g., Fast Lomb-Scargle or limiting frequencies) for $N > 10,000$.

#### B. IAAFT (For Even Sampling)
*   **Methodology:** Iteratively adjusts the Fourier phases and amplitudes to match both the power spectrum and the value distribution of the original data.
*   **Pros:** Preserves both linear correlation and marginal distribution. Fast ($O(N \log N)$ via FFT).
*   **Cons:** Assumes even sampling.

#### C. CAR(1) Model (Parametric Alternative)
*   **Methodology:** Fits a Continuous AR(1) process ($dX_t = -\alpha X_t dt + \sigma dW_t$) to the data and simulates paths.
*   **Pros:** Very fast; handles uneven sampling naturally.
*   **Cons:** Parametric (assumes a specific noise process); may not capture complex spectral features.

## Integration Strategy

*   **Module:** Create a new module `MannKS/_surrogate.py`.
*   **Dependencies:** `scipy.signal` (Lomb-Scargle), `numpy.fft` (IAAFT).
*   **Public API:**
    *   Expose `surrogate_test` in `__init__.py`.
    *   Add a `surrogate_method` argument to `trend_test` to optionally trigger this check alongside the standard test.
    *   Return a `p_surrogate` value in the results tuple.

## Performance Considerations

*   **Large Datasets ($N > 5,000$):**
    *   Lomb-Scargle is slow. For large $N$, we may need to:
        *   Use a "Fast Lomb-Scargle" implementation (O(N log N) using FFT on a grid).
        *   Downsample the frequency grid.
        *   Default to CAR(1) for speed if `method='auto'`.
*   **Parallelization:** Surrogate generation and MK calculation are trivially parallelizable.

## Validation Strategy

1.  **Null Case:** Generate pure Red Noise (AR(1)) with no trend. Verify that the surrogate test correctly rejects the trend (high p-value) while standard MK might falsely detect one.
2.  **Trend Case:** Add a known linear trend to Red Noise. Verify that surrogates detect the trend (low p-value).
3.  **Irregular Sampling:** Randomly remove 50% of points from a regular series and verify Lomb-Scargle performance vs. IAAFT (which would fail or require interpolation).

## Implementation Steps

1.  Implement `_lomb_scargle_surrogates` in `_surrogate.py`.
2.  Implement `_iaaft_surrogates` in `_surrogate.py`.
3.  Implement `surrogate_test` wrapper.
4.  Integrate into `trend_test`.
5.  Add comprehensive tests in `tests/test_surrogate.py`.
6.  Update documentation and tutorials.
