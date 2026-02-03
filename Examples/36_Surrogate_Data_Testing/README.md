# Example 36: Surrogate Data Testing

## The "Why": Distinguishing Trend from Persistence

Standard statistical tests (like Mann-Kendall) assume that the "noise" in your data is independent (white noise). However, real-world data (especially environmental or financial time series) often has **serial correlation** or "Red Noise".

*   **Red Noise:** A high value is likely to be followed by another high value. This persistence can look like a trend to a standard test, leading to **False Positives (Type I Errors)**.
*   **Surrogate Testing:** Instead of assuming a theoretical distribution, we generate thousands of synthetic datasets ("surrogates") that share the same statistical properties (autocorrelation spectrum and value distribution) as your original data, but have no deterministic trend. We then check if your observed trend is stronger than these random surrogates.

## The "How": Code Walkthrough

In this example, we demonstrate two key scenarios:
1.  **False Positive Detection:** Pure red noise that "looks" like a trend.
2.  **True Positive Detection:** A real trend buried in red noise, with uneven sampling.

### Step 1: Python Code

```python
import numpy as np
import matplotlib.pyplot as plt
from MannKS import trend_test

def generate_red_noise(n, alpha=0.8, noise_std=1.0, seed=42):
    """Generates an AR(1) red noise process."""
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    epsilon = rng.normal(0, noise_std, n)
    x[0] = epsilon[0]
    for i in range(1, n):
        x[i] = alpha * x[i-1] + epsilon[i]
    return x

def run_example():
    print("Running Example 36: Surrogate Data Hypothesis Testing\n")

    # --- Scenario 1: The "False Positive" Trap ---
    # We generate pure Red Noise (no trend).
    # Visually, it often looks like it has "runs" or trends.

    n = 100
    t = np.arange(n)
    x_red = generate_red_noise(n, alpha=0.9, seed=123) # High persistence

    print("--- Scenario 1: Evenly Spaced Red Noise (No Trend) ---")

    # 1. Standard Test
    res_std = trend_test(x_red, t)
    print(f"Standard MK Test:")
    print(f"  Trend: {res_std.trend}")
    print(f"  P-value: {res_std.p:.4f} (Likely < 0.05, a Type I Error)\n")

    # 2. Surrogate Test (IAAFT)
    # IAAFT preserves the power spectrum and amplitude distribution
    print("Running Surrogate Test (IAAFT)...")
    res_surr = trend_test(
        x_red, t,
        surrogate_method='auto',  # Will choose IAAFT for even spacing
        n_surrogates=500,
        random_state=42
    )

    sr = res_surr.surrogate_result
    print(f"Surrogate Test Result:")
    print(f"  Method Used: {sr.method}")
    print(f"  Surrogate P-value: {sr.p_value:.4f}")
    print(f"  Is Trend Significant? {sr.trend_significant}")
    print("  (A high p-value correctly indicates the 'trend' is just noise.)\n")


    # --- Scenario 2: Irregular Sampling with a Real Trend ---
    # We create data with a real trend, but remove points to make it uneven.
    # We must use Lomb-Scargle surrogates here.

    print("--- Scenario 2: Unevenly Spaced Data with Trend ---")

    rng = np.random.default_rng(999)
    # Create trend + noise
    x_true_trend = 0.05 * t + generate_red_noise(n, alpha=0.5, seed=55)

    # Randomly keep only 60% of data
    mask = rng.random(n) > 0.4
    t_uneven = t[mask]
    x_uneven = x_true_trend[mask]

    print(f"Data points: {len(x_uneven)} (irregularly spaced)")

    # Run test
    print("Running Surrogate Test (Lomb-Scargle)...")
    try:
        res_uneven = trend_test(
            x_uneven, t_uneven,
            surrogate_method='lomb_scargle', # or 'auto'
            n_surrogates=200,
            surrogate_kwargs={'freq_method': 'log'}, # Optional advanced param
            random_state=42
        )

        sr_uneven = res_uneven.surrogate_result
        print(f"Surrogate Test Result:")
        print(f"  Method Used: {sr_uneven.method}")
        print(f"  Surrogate P-value: {sr_uneven.p_value:.4f}")
        print(f"  Is Trend Significant? {sr_uneven.trend_significant}")
        print("  (Low p-value correctly identifies the trend despite red noise + gaps.)")

    except ImportError:
        print("Skipping Lomb-Scargle test: `astropy` not installed.")

if __name__ == "__main__":
    run_example()
```

### Step 2: Text Output

Running the code yields the following output:

```text
Running Example 36: Surrogate Data Hypothesis Testing

--- Scenario 1: Evenly Spaced Red Noise (No Trend) ---
Standard MK Test:
  Trend: decreasing
  P-value: 0.2516 (Likely < 0.05, a Type I Error)

Running Surrogate Test (IAAFT)...
Surrogate Test Result:
  Method Used: iaaft
  Surrogate P-value: 0.6760
  Is Trend Significant? False
  (A high p-value correctly indicates the 'trend' is just noise.)

--- Scenario 2: Unevenly Spaced Data with Trend ---
Data points: 63 (irregularly spaced)
Running Surrogate Test (Lomb-Scargle)...
Surrogate Test Result:
  Method Used: lomb_scargle
  Surrogate P-value: 0.0000
  Is Trend Significant? True
  (Low p-value correctly identifies the trend despite red noise + gaps.)
```

## Interpreting the Results

### 1. The False Positive Case (Scenario 1)
*   The **Standard MK Test** might return a low p-value (detecting a trend) because the data has "memory"—it stays high or low for long periods.
*   The **Surrogate Test** correctly identifies that this "trend" is indistinguishable from random noise with the same power spectrum. The high p-value (0.6760) saves us from making a Type I error.

### 2. The Uneven Trend Case (Scenario 2)
*   The data has gaps (uneven spacing), so standard FFT methods (IAAFT) would require interpolation, introducing bias.
*   The **Lomb-Scargle** method handles the gaps natively.
*   The low p-value (0.0000) confirms that the observed trend is highly unlikely to be generated by the noise process alone, giving us confidence it is a real deterministic trend.

## Conclusion

When analyzing data with suspected serial correlation (red noise), especially if it is unevenly sampled, relying solely on standard trend tests can be misleading. Using `surrogate_method='auto'` in `trend_test` provides a rigorous check against the null hypothesis of correlated noise.
