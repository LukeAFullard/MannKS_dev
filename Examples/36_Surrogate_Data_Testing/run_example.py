"""
Example 36: Surrogate Data Testing
----------------------------------
This example demonstrates how to use surrogate data methods (IAAFT and Lomb-Scargle)
to test for trends in the presence of "Red Noise" (serial correlation).

Standard Mann-Kendall tests assume independence. If your data has strong persistence
(like many climate or financial variables), standard tests may generate false positives.
Surrogate tests compare your trend against thousands of synthetic "noise" datasets
that share the same statistical properties as your original data.
"""

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

    print("\n--- DISCUSSION: Consequences of Results ---")
    print("1. If Null Hypothesis is Rejected (Significant Result):")
    print("   - Conclusion: The observed trend is unlikely to be a random fluctuation of the background noise.")
    print("   - Action: You can confidently quantify the trend using Sen's Slope.")
    print("   - Implication: The trend is 'robust' against serial correlation.")

    print("\n2. If Null Hypothesis is Accepted (Not Significant):")
    print("   - Conclusion: The observed 'trend' is indistinguishable from random colored noise.")
    print("   - Action: Do NOT claim a deterministic trend. Treat the finding as spurious or inconclusive.")
    print("   - Implication: Any standard MK p-value < 0.05 was likely a Type I error driven by persistence.")

if __name__ == "__main__":
    run_example()
