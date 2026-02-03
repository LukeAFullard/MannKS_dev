# Example 36: Surrogate Data Testing

This example demonstrates how to use the new **Surrogate Data Hypothesis Testing** features introduced in v0.6.0.

## Why Surrogate Data?

Standard statistical tests (like Mann-Kendall) assume that the "noise" in your data is independent (white noise). However, real-world data (especially environmental or financial time series) often has **serial correlation** or "Red Noise".

*   **Red Noise:** A high value is likely to be followed by another high value. This persistence can look like a trend to a standard test, leading to **False Positives (Type I Errors)**.
*   **Surrogate Testing:** Instead of assuming a theoretical distribution, we generate thousands of synthetic datasets ("surrogates") that share the same statistical properties (autocorrelation spectrum and value distribution) as your original data, but have no deterministic trend. We then check if your observed trend is stronger than these random surrogates.

## Methods Demonstrated

1.  **IAAFT (Iterated Amplitude Adjusted Fourier Transform):**
    *   Used for **evenly spaced** data.
    *   Preserves the power spectrum and the exact values of the original data.

2.  **Lomb-Scargle Spectral Synthesis:**
    *   Used for **unevenly spaced** data (missing values, irregular observations).
    *   Uses Astropy to estimate the spectrum without interpolation artifacts.

## Running the Example

```bash
python run_example.py
```

## Key Code Snippet

```python
# To enable surrogate testing, simply add the parameter:
result = trend_test(
    x, t,
    surrogate_method='auto',  # Automatically picks IAAFT or Lomb-Scargle
    n_surrogates=1000
)

# Access results
if result.surrogate_result:
    print(f"Surrogate P-value: {result.surrogate_result.p_value}")
```
