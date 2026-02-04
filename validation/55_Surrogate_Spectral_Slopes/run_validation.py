
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
        f.write("# Validation Report: Surrogate Data Spectral Slopes\n\n")
        f.write("Testing Mann-Kendall vs Surrogate Test False Positive Rates across different spectral colors (Beta).\n")
        f.write("Beta = 0 (White), 1 (Pink), 2 (Red/Brownian).\n\n")
        f.write("| Test Name | Status | Message | Details |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            details_str = ", ".join([f"{k}={v}" for k, v in r.details.items()])
            f.write(f"| {r.name} | **{r.status}** | {r.message} | {details_str} |\n")

    print(f"Report saved to {md_path}")

def generate_colored_noise(n, beta, seed=None):
    """
    Generate colored noise with power spectrum P(f) ~ 1/f^beta.
    Uses FFT filtering of white noise.
    """
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n)

    # Go to frequency domain
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(n)

    # Scale amplitudes: A ~ sqrt(P) ~ f^(-beta/2)
    # Avoid division by zero at DC (index 0)
    scaling = np.ones_like(freqs)
    if beta != 0:
        with np.errstate(divide='ignore'):
             scaling[1:] = freqs[1:] ** (-beta / 2.0)

    X = X * scaling
    X[0] = 0 # Remove DC component (zero mean)

    # Back to time domain
    y = np.fft.irfft(X, n=n)

    # Normalize to unit variance for consistency
    if np.std(y) > 0:
        y = y / np.std(y)

    return y

def validate_spectral_slopes():
    results = []

    # Beta from 0 to 2.5 step 0.25
    betas = np.arange(0, 2.75, 0.25)

    # Parameters
    n_points = 100
    n_sims = 50       # Number of simulations per beta to estimate rejection rate
    n_surrogates = 200 # Surrogates per test
    alpha = 0.05

    print(f"Starting Monte Carlo: {len(betas)} betas, {n_sims} sims each, {n_surrogates} surrogates.")

    for beta in betas:
        beta = round(beta, 2)
        rejections_mk = 0
        rejections_surr = 0

        for i in range(n_sims):
            seed = int(beta * 10000 + i)
            # Generate null data (colored noise, no trend)
            y = generate_colored_noise(n_points, beta, seed=seed)
            t = np.arange(n_points)

            # Run test
            # Suppress warnings about IAAFT/etc if any (though we pass even data)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                res = trend_test(
                    y, t,
                    surrogate_method='iaaft',
                    n_surrogates=n_surrogates,
                    random_state=seed
                )

            # Check rejections (False Positives)
            if res.p < alpha:
                rejections_mk += 1

            if res.surrogate_result.p_value < alpha:
                rejections_surr += 1

        rate_mk = rejections_mk / n_sims
        rate_surr = rejections_surr / n_sims

        # Assessment
        status = "PASS"

        # 1. Surrogate Test should control Type I error (approx alpha)
        # Allow some fluctuation due to limited M=50. Say < 0.20 is acceptable "control" vs runaway.
        # Ideally it should be near 0.05.
        if rate_surr > 0.20:
            status = "WARN"

        # 2. Standard MK should break down as Beta increases
        # For Beta > 1.5, we expect MK to have high false positive rates.
        # Just logging this, not necessarily a failure of the library (it's a failure of the method).
        # But we want to confirm that Surrogate < MK for high betas.
        if beta >= 1.0 and rate_surr >= rate_mk:
             # If surrogates are WORSE or EQUAL to MK when MK is bad, that's an issue.
             # Unless MK is good (rate_mk low).
             if rate_mk > 0.20:
                 status = "FAIL"

        msg = f"Beta={beta:.2f}: MK Rej={rate_mk:.2f}, Surr Rej={rate_surr:.2f}"
        print(msg)

        results.append(ValidationResult(
            f"Spectral Slope Beta={beta}",
            status,
            msg,
            {"beta": beta, "mk_rejection_rate": rate_mk, "surr_rejection_rate": rate_surr}
        ))

    return results

if __name__ == "__main__":
    run_validation_suite(validate_spectral_slopes)
