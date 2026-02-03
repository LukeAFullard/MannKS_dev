
import numpy as np
import pandas as pd
import warnings
import sys
import os

# Ensure MannKS is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from MannKS import trend_test

class ValidationResult:
    def __init__(self, name, status, message, details=None):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}

    def to_dict(self):
        return {
            'Test Name': self.name,
            'Status': self.status,
            'Message': self.message,
            **self.details
        }

def run_validation_suite(validation_func):
    print("Running validation suite...")
    results = validation_func()

    df = pd.DataFrame([r.to_dict() for r in results])

    output_dir = os.path.dirname(__file__)
    csv_path = os.path.join(output_dir, 'validation_results.csv')
    md_path = os.path.join(output_dir, 'README.md')

    # Save CSV
    df.to_csv(csv_path, index=False)
    print(f"Results saved to {csv_path}")

    # Save Markdown Report
    with open(md_path, 'w') as f:
        f.write("# Validation Report: Surrogate Data Methods\n\n")
        f.write("| Test Name | Status | Message | Details |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            details_str = ", ".join([f"{k}={v}" for k, v in r.details.items()])
            f.write(f"| {r.name} | **{r.status}** | {r.message} | {details_str} |\n")

    print(f"Report saved to {md_path}")

def generate_red_noise(n, alpha=0.7, random_state=None):
    """Generate AR(1) red noise: x_t = alpha * x_{t-1} + epsilon_t"""
    rng = np.random.default_rng(random_state)
    x = np.zeros(n)
    epsilon = rng.standard_normal(n)
    x[0] = epsilon[0]
    for t in range(1, n):
        x[t] = alpha * x[t-1] + epsilon[t]
    return x

def validate_surrogate_methods():
    results = []

    # --- Case 1: Pure Red Noise (Null Hypothesis) ---
    # Standard MK often fails here (Type I error) due to serial correlation.
    # Surrogate test should correctly find NO significance (high p-value).

    n = 200
    t = np.arange(n)
    # Use a seed where MK typically fails (finds a trend) but surrogates save us
    # This specific seed produces a "random walk" that looks like a trend
    x_null = generate_red_noise(n, alpha=0.8, random_state=123)

    res_null = trend_test(x_null, t, surrogate_method='iaaft', n_surrogates=500, random_state=42)

    # Check standard MK (might be significant due to autocorrelation)
    mk_p = res_null.p

    # Check Surrogate (should NOT be significant)
    surr_p = res_null.surrogate_result.p_value

    status_null = "PASS" if surr_p > 0.05 else "FAIL"
    msg_null = f"Null Case: MK p={mk_p:.3f}, Surrogate p={surr_p:.3f} (>0.05 expected)"

    results.append(ValidationResult(
        "Red Noise Null Rejection",
        status_null,
        msg_null,
        {"mk_p": mk_p, "surr_p": surr_p}
    ))

    # --- Case 2: Red Noise + Trend (Alternative Hypothesis) ---
    # Surrogate test should correctly find significance.

    trend = 0.05 * t # Strong trend
    x_trend = generate_red_noise(n, alpha=0.8, random_state=456) + trend

    res_trend = trend_test(x_trend, t, surrogate_method='iaaft', n_surrogates=500, random_state=42)

    surr_p_trend = res_trend.surrogate_result.p_value

    status_trend = "PASS" if surr_p_trend < 0.05 else "FAIL"
    msg_trend = f"Trend Case: Surrogate p={surr_p_trend:.3f} (<0.05 expected)"

    results.append(ValidationResult(
        "Red Noise Trend Detection",
        status_trend,
        msg_trend,
        {"surr_p": surr_p_trend}
    ))

    # --- Case 3: Uneven Sampling (Lomb-Scargle) ---
    # Randomly remove 40% of points to create irregular spacing

    rng = np.random.default_rng(789)
    mask = rng.random(n) > 0.4
    t_uneven = t[mask]
    x_uneven = x_trend[mask] # Still has the trend

    res_uneven = trend_test(x_uneven, t_uneven, surrogate_method='lomb_scargle', n_surrogates=200, random_state=42)

    surr_p_uneven = res_uneven.surrogate_result.p_value
    method_used = res_uneven.surrogate_result.method

    status_uneven = "PASS" if (surr_p_uneven < 0.05 and method_used == 'lomb_scargle') else "FAIL"
    msg_uneven = f"Uneven Case: Method={method_used}, p={surr_p_uneven:.3f}"

    results.append(ValidationResult(
        "Lomb-Scargle Uneven Detection",
        status_uneven,
        msg_uneven,
        {"method": method_used, "surr_p": surr_p_uneven}
    ))

    return results

if __name__ == "__main__":
    run_validation_suite(validate_surrogate_methods)
