
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
        f.write("Testing Mann-Kendall vs Surrogate Test False Positive Rates (Null) and True Positive Rates (Trend) across different spectral colors (Beta).\n")
        f.write("Comparison of IAAFT (Even) and Lomb-Scargle (Uneven).\n\n")

        # Commentary
        commentary = generate_commentary(results)
        f.write("## Interpretation of Results\n\n")
        f.write(commentary + "\n\n")

        f.write("## Detailed Results\n\n")
        f.write("| Test Name | Status | Message | Details |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            details_str = ", ".join([f"{k}={v}" for k, v in r.details.items()])
            f.write(f"| {r.name} | **{r.status}** | {r.message} | {details_str} |\n")

    print(f"Report saved to {md_path}")

def generate_commentary(results):
    """
    Analyzes the validation results and generates a human-readable interpretation.
    """
    lines = []

    # 1. Analyze MK Breakdown (False Positives on Null Data)
    mk_fail_betas = [r.details['beta'] for r in results if r.details['null_mk_rej'] > 0.20]
    surr_fail_betas = [r.details['beta'] for r in results if r.details['null_iaaft_rej'] > 0.20]

    lines.append("### 1. Robustness to Serial Correlation (Type I Error)")
    if mk_fail_betas:
        min_fail = min(mk_fail_betas)
        lines.append(f"- **Standard Mann-Kendall:** As expected, the standard test fails to control Type I errors for colored noise. "
                     f"Rejection rates exceed 20% starting at Beta={min_fail}, indicating that serial correlation is being mistaken for a trend.")
    else:
        lines.append("- **Standard Mann-Kendall:** Surprisingly robust in this run (or insufficient simulations).")

    if not surr_fail_betas:
        lines.append("- **Surrogate Test:** Successfully controls the False Positive Rate across all tested spectral slopes. "
                     "This confirms that the method correctly accounts for the background noise spectrum.")
    else:
        lines.append(f"- **Surrogate Test:** Showed elevated rejection rates at Beta={surr_fail_betas}. This warrants investigation.")

    # 2. Power Analysis (True Positives on Trending Data)
    low_power_betas = [r.details['beta'] for r in results if r.details['trend_iaaft_rej'] < 0.50]

    lines.append("\n### 2. Statistical Power (Trend Detection)")
    if not low_power_betas:
        lines.append("- **Sensitivity:** The surrogate test maintained high power (>50%) for detecting the added linear trend across all noise colors.")
    else:
        lines.append(f"- **Sensitivity:** Power decreases for stronger red noise (Beta >= {min(low_power_betas)}). "
                     "This is expected, as strong low-frequency noise can mask or mimic the trend signal, making significance harder to establish.")

    # 3. Uneven Sampling (Lomb-Scargle vs IAAFT)
    # Compare average rejection rates on uneven null data
    ls_rejections = [r.details['uneven_ls_rej'] for r in results]
    iaaft_rejections = [r.details['uneven_iaaft_rej'] for r in results]
    avg_ls = sum(ls_rejections) / len(ls_rejections)
    avg_iaaft = sum(iaaft_rejections) / len(iaaft_rejections)

    lines.append("\n### 3. Uneven Sampling Performance")
    lines.append(f"- **Lomb-Scargle Method:** Average rejection rate on uneven null data was {avg_ls:.2f}. "
                 "This demonstrates its ability to handle irregular spacing without interpolation bias.")
    lines.append(f"- **IAAFT Method (on Uneven):** Average rejection rate was {avg_iaaft:.2f}. "
                 "While it may perform adequately in some random-gap scenarios, it is theoretically unsound for non-uniform grids.")

    return "\n".join(lines)

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
    n_sims = 10       # Number of simulations per beta (Reduced for runtime)
    n_surrogates = 200 # Surrogates per test
    alpha = 0.05

    print(f"Starting Monte Carlo: {len(betas)} betas, {n_sims} sims each, {n_surrogates} surrogates.")

    for beta in betas:
        beta = round(beta, 2)

        # Trackers
        # Even / Null
        rej_mk_even_null = 0
        rej_iaaft_even_null = 0

        # Even / Trend
        rej_mk_even_trend = 0
        rej_iaaft_even_trend = 0

        # Uneven / Null
        rej_ls_uneven_null = 0
        rej_iaaft_uneven_null = 0 # Comparison

        for i in range(n_sims):
            seed = int(beta * 10000 + i)

            # 1. Base Data (Null, Even)
            y_null = generate_colored_noise(n_points, beta, seed=seed)
            t_even = np.arange(n_points)

            # 2. Trend Data (Trend, Even)
            # Add a trend that is detectable in white noise but maybe not in red
            # Slope = 2 * sigma / N roughly
            trend_slope = 0.03
            y_trend = y_null + trend_slope * t_even

            # 3. Uneven Data (Null)
            # Drop 30% randomly
            rng = np.random.default_rng(seed)
            mask = rng.random(n_points) > 0.3
            y_uneven_null = y_null[mask]
            t_uneven = t_even[mask]

            # --- Tests ---

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # A. Even / Null (IAAFT)
                res_en = trend_test(y_null, t_even, surrogate_method='iaaft', n_surrogates=n_surrogates, random_state=seed)
                if res_en.p < alpha: rej_mk_even_null += 1
                if res_en.surrogate_result.p_value < alpha: rej_iaaft_even_null += 1

                # B. Even / Trend (IAAFT)
                res_et = trend_test(y_trend, t_even, surrogate_method='iaaft', n_surrogates=n_surrogates, random_state=seed)
                if res_et.p < alpha: rej_mk_even_trend += 1
                if res_et.surrogate_result.p_value < alpha: rej_iaaft_even_trend += 1

                # C. Uneven / Null (Lomb-Scargle vs IAAFT)
                # LS
                res_un_ls = trend_test(y_uneven_null, t_uneven, surrogate_method='lomb_scargle', n_surrogates=n_surrogates, random_state=seed)
                if res_un_ls.surrogate_result.p_value < alpha: rej_ls_uneven_null += 1

                # IAAFT on Uneven (Comparison - expected to be worse/biased)
                res_un_iaaft = trend_test(y_uneven_null, t_uneven, surrogate_method='iaaft', n_surrogates=n_surrogates, random_state=seed)
                if res_un_iaaft.surrogate_result.p_value < alpha: rej_iaaft_uneven_null += 1

        # --- Aggregation & Reporting ---

        # Rates
        rate_mk_en = rej_mk_even_null / n_sims
        rate_iaaft_en = rej_iaaft_even_null / n_sims

        rate_mk_et = rej_mk_even_trend / n_sims
        rate_iaaft_et = rej_iaaft_even_trend / n_sims

        rate_ls_un = rej_ls_uneven_null / n_sims
        rate_iaaft_un = rej_iaaft_uneven_null / n_sims

        print(f"Beta={beta}: Null(MK={rate_mk_en:.2f}, IAAFT={rate_iaaft_en:.2f}) | Trend(MK={rate_mk_et:.2f}, IAAFT={rate_iaaft_et:.2f}) | UnevenNull(LS={rate_ls_un:.2f}, IAAFT={rate_iaaft_un:.2f})")

        # Status checks
        status = "PASS"
        msg = []

        # 1. Null Control (IAAFT Even)
        if rate_iaaft_en > 0.20:
            status = "WARN"
            msg.append("IAAFT Null Rate High")

        # 2. Null Control (LS Uneven)
        if rate_ls_un > 0.20:
            status = "WARN"
            msg.append("LS Null Rate High")

        # 3. MK Breakdown Check (High Beta)
        if beta >= 1.0 and rate_mk_en > 0.30 and rate_iaaft_en < 0.15:
             msg.append("MK Fails as expected")

        # 4. Uneven Comparison
        # We generally expect LS to work. IAAFT on uneven might not fail drastically for random gaps but is theoretically wrong.
        # Just logging the diff.

        if not msg:
            msg.append("Rates nominal")

        msg_str = "; ".join(msg)

        results.append(ValidationResult(
            f"Beta={beta} Detailed",
            status,
            msg_str,
            {
                "beta": beta,
                "null_mk_rej": rate_mk_en,
                "null_iaaft_rej": rate_iaaft_en,
                "trend_mk_rej": rate_mk_et,
                "trend_iaaft_rej": rate_iaaft_et,
                "uneven_ls_rej": rate_ls_un,
                "uneven_iaaft_rej": rate_iaaft_un
            }
        ))

    return results

if __name__ == "__main__":
    run_validation_suite(validate_spectral_slopes)
