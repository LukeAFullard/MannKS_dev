# v0.6.0 Audit Findings

## Critical Bugs

### 1. Shape Mismatch in `seasonal_trend_test` with `dy`
When performing a seasonal trend test with surrogate data, if the user provides measurement uncertainties (`dy`) via `surrogate_kwargs`, the function fails with a `ValueError: shape mismatch`.

**Cause:**
The `seasonal_trend_test` function iterates over seasons and calls `surrogate_test` for each season. However, it passes the `surrogate_kwargs` dictionary (containing the full-length `dy` array) directly to each seasonal call. The `surrogate_test` function then passes this full-length `dy` to `LombScargle`, which expects `dy` to match the length of the seasonal data subset.

**Reproduction:**
```python
seasonal_trend_test(x, t, period=12, surrogate_method='lomb_scargle',
                    surrogate_kwargs={'dy': full_length_errors})
```

### 2. Shape Mismatch in `trend_test` with `dy` and Filtered Data
When performing a standard trend test, if the input data requires filtering (e.g., contains NaNs) and `dy` is provided in `surrogate_kwargs`, the function fails with a `ValueError: shape mismatch`.

**Cause:**
`trend_test` filters the input `x` and `t` (via `_prepare_data`) to remove NaNs. However, the `dy` array inside `surrogate_kwargs` remains at its original length. When `surrogate_test` is called with the filtered `x`/`t` and the original `dy`, `LombScargle` raises a shape mismatch error.

## Limitations & Observations

### 1. Spectral Whitening in Lomb-Scargle Surrogates
The `_lomb_scargle_surrogates` implementation follows an Amplitude Adjusted Fourier Transform (AAFT) approach but is **non-iterative**.
- It generates surrogates by spectral synthesis (preserving the periodogram).
- It then rank-adjusts the result to match the original amplitude distribution.
- **Impact:** For highly non-Gaussian signals (e.g., pure sine waves), the rank adjustment distorts the spectrum ("whitening"), potentially shifting the dominant frequency peak or introducing harmonics.
- **Context:** This is generally acceptable for the primary use case of testing against Gaussian Red Noise, but users should be aware that spectral properties are not strictly preserved for non-Gaussian processes.

### 2. Censored Data Approximation
Surrogate data generation currently treats censored values (detection limits) as continuous observed values. The `surrogate_test` function issues a warning: "Censored data: surrogates treated as uncensored". This is a documented limitation but implies that the null distribution may be biased if censoring is heavy.

## Recommendations

1.  **Fix `seasonal_trend_test`**: Logic must be added to slice array-like arguments in `surrogate_kwargs` (like `dy`) to match the seasonal mask before calling `surrogate_test`.
2.  **Fix `trend_test`**: Logic must be added to filter array-like arguments in `surrogate_kwargs` to match the `_prepare_data` filtering (NaN removal).
3.  **Documentation**: Explicitly clarify in the `_lomb_scargle_surrogates` docstring that it is a non-iterative AAFT method and may not fully preserve spectra for non-Gaussian data.
