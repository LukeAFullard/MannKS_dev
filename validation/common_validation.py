
import os
import sys
import numpy as np
import pandas as pd
import time
import logging
import warnings
import piecewise_regression
from MannKS._scout import RobustSegmentedTrend
from MannKS._hybrid import HybridSegmentedTrend

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup Logging
def setup_logging(output_dir):
    log_file = os.path.join(output_dir, 'validation_log.txt')
    # Clear old log
    if os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger()

# --- 1. OLS Piecewise Implementation (piecewise-regression) ---
def fit_piecewise_ols(t, y, max_breakpoints=2):
    """
    Fits piecewise linear regression using the piecewise_regression library.
    Searches for 0, 1, ..., max_breakpoints and selects best via BIC.
    """
    n = len(y)
    best_bic = np.inf
    best_n = 0
    best_bps = []

    # 0 Breakpoints (Linear) - Manually calculate BIC as Fit doesn't support n_breakpoints=0
    # y = a + b*t
    A = np.vstack([t, np.ones(n)]).T
    try:
        sol, resid, _, _ = np.linalg.lstsq(A, y, rcond=None)
        if resid.size > 0:
            ssr = resid[0]
        else:
            # Perfect fit
            y_pred = sol[0]*t + sol[1]
            ssr = np.sum((y - y_pred)**2)

        # k = 3 for BIC usually (intercept, slope, variance estimate), but for consistency with package:
        # piecewise_regression uses k = 2 * n_breakpoints + 2 usually?
        # Let's check package implementation if possible, or stick to standard BIC definition.
        # piecewise_regression uses: bic = n * log(rss/n) + k * log(n)
        # where k = number of params. For linear: intercept, slope. k=2.

        k = 2
        if ssr <= 1e-10: ssr = 1e-10
        bic = n * np.log(ssr/n) + k * np.log(n)

        best_bic = bic
        best_n = 0
        best_bps = []
    except:
        pass

    # Loop for 1 to max_breakpoints
    best_slopes = []

    for n_bp in range(1, max_breakpoints + 1):
        try:
            pw_fit = piecewise_regression.Fit(t, y, n_breakpoints=n_bp, verbose=False)

            # Access results via best_muggeo as requested for robust estimate access
            if hasattr(pw_fit, 'best_muggeo') and hasattr(pw_fit.best_muggeo, 'best_fit'):
                 best_fit = pw_fit.best_muggeo.best_fit

                 # BIC
                 # Use the library's calculated BIC directly if available
                 if hasattr(best_fit, 'bic'):
                     current_bic = best_fit.bic
                 else:
                     # Fallback calculation
                     rss = getattr(best_fit, 'residual_sum_squares', None)
                     if rss is None:
                         # Try finding it in dict if it's not an attribute
                         rss = getattr(best_fit, 'rss', np.inf)

                     k = 2 * n_bp + 2
                     if rss <= 1e-10: rss = 1e-10
                     current_bic = n * np.log(rss/n) + k * np.log(n)

                 if current_bic < best_bic:
                    best_bic = current_bic
                    best_n = n_bp

                    # Extract breakpoints from estimates
                    estimates = best_fit.estimates
                    bps = []
                    for key, val in estimates.items():
                        if key.startswith('breakpoint'):
                            bps.append(val['estimate'])
                    best_bps = sorted(bps)

                    # Extract slopes
                    # piecewise_regression gives beta1, alpha1, alpha2...
                    # Slope 1 = beta1
                    # Slope 2 = beta1 + alpha1
                    # Slope k = beta1 + sum(alpha1..alpha_k-1)
                    slopes = []
                    # Get beta1
                    beta1_est = estimates.get('beta1', {}).get('estimate', np.nan)
                    slopes.append(beta1_est)

                    current_slope = beta1_est
                    for i in range(1, n_bp + 1):
                        alpha_key = f'alpha{i}'
                        alpha_est = estimates.get(alpha_key, {}).get('estimate', 0.0)
                        current_slope += alpha_est
                        slopes.append(current_slope)
                    best_slopes = slopes

            else:
                 # Fallback to standard get_results if best_muggeo fails (though it shouldn't)
                 res = pw_fit.get_results()
                 current_bic = res.get('bic')
                 if current_bic is not None and current_bic < best_bic:
                    best_bic = current_bic
                    best_n = n_bp
                    best_bps = res['estimates']['breakpoints']
                    # Slope extraction fallback (similar logic but from res['estimates'])
                    slopes = []
                    estimates = res['estimates']
                    beta1_est = estimates.get('beta1', {}).get('estimate', np.nan)
                    slopes.append(beta1_est)
                    current_slope = beta1_est
                    for i in range(1, n_bp + 1):
                        alpha_key = f'alpha{i}'
                        alpha_est = estimates.get(alpha_key, {}).get('estimate', 0.0)
                        current_slope += alpha_est
                        slopes.append(current_slope)
                    best_slopes = slopes

        except Exception:
            # Convergence failure or other error
            continue

    if best_n == 0:
        # Get linear slope for N=0
        try:
            p = np.polyfit(t, y, 1)
            best_slopes = [p[0]]
        except:
            best_slopes = [np.nan]

    return best_n, best_bps, best_slopes

# --- 2. Generic Run Function ---
def run_validation_suite(data_generator, output_dir, n_iterations=100):
    logger = setup_logging(output_dir)
    logger.info(f"Starting validation suite with {n_iterations} iterations.")

    results = []

    # Define methods
    # Comparing Piecewise-Regression (OLS) vs MannKS Robust vs MannKS Hybrid
    methods = [
        ('Piecewise_Regression', 'ols', {}),
        ('MannKS_BIC', 'mannks_robust', {'criterion': 'bic'}),
        ('MannKS_Hybrid', 'mannks_hybrid', {})
    ]

    start_total = time.time()

    for i in range(n_iterations):
        gen_data = data_generator(seed=42+i)
        t, x, true_n, true_bps = gen_data[:4]

        true_slopes = None
        if len(gen_data) >= 5:
            true_slopes = gen_data[4]

        iter_res = {
            'iter': i,
            'true_n': true_n,
            'true_bps': str(list(true_bps))
        }

        if i % 10 == 0:
            logger.info(f"Processing iteration {i}/{n_iterations}...")

        for name, m_type, kwargs in methods:
            t0 = time.time()
            pred_slopes = []
            try:
                if m_type == 'ols':
                    pred_n, pred_bps, pred_slopes = fit_piecewise_ols(t, x, max_breakpoints=2)
                elif m_type == 'mannks_robust':
                    criterion = kwargs.get('criterion', 'bic')

                    best_score = np.inf
                    best_n = 0
                    best_bps = []
                    previous_bps = None
                    best_model = None

                    # Scan N=0, 1, 2
                    for n_bp in range(3):
                        model = RobustSegmentedTrend(n_breakpoints=n_bp)
                        model.fit(t, x, initial_guess=previous_bps)

                        # Update previous_bps for next iteration (greedy strategy)
                        if n_bp > 0:
                            previous_bps = model.breakpoints_

                        y_pred = model.predict(t)
                        resids = x - y_pred
                        ssr = np.sum(resids**2)
                        if ssr <= 1e-10: ssr = 1e-10

                        n_samples = len(x)
                        # k = 2 for N=0 (intercept, slope)
                        # k = 4 for N=1 (int, slope1, slope2/alpha, bp)
                        # k = 6 for N=2
                        k = 2 + 2 * n_bp

                        if criterion == 'aic':
                            # AIC = n * ln(RSS/n) + 2k
                            score = n_samples * np.log(ssr/n_samples) + 2 * k
                        elif criterion == 'mbic':
                            # mBIC (Modified BIC for changepoints)
                            k_mbic = 2 + 3 * n_bp
                            score = n_samples * np.log(ssr/n_samples) + k_mbic * np.log(n_samples)
                        elif criterion == 'aicc':
                            # AICc = AIC + 2k(k+1)/(n-k-1)
                            aic = n_samples * np.log(ssr/n_samples) + 2 * k
                            denom = n_samples - k - 1
                            if denom > 0:
                                score = aic + (2 * k * (k + 1)) / denom
                            else:
                                score = np.inf # Penalize invalid model for small N
                        elif criterion == 'hqc':
                            # HQC = n * ln(RSS/n) + 2k * ln(ln(n))
                            score = n_samples * np.log(ssr/n_samples) + 2 * k * np.log(np.log(n_samples))
                        else: # bic
                            # BIC = n * ln(RSS/n) + k * ln(n)
                            score = n_samples * np.log(ssr/n_samples) + k * np.log(n_samples)

                        if score < best_score:
                            best_score = score
                            best_n = n_bp
                            best_bps = model.breakpoints_
                            best_model = model

                    pred_n = best_n
                    pred_bps = list(best_bps) if best_bps is not None else []

                    # Extract slopes from best model
                    if best_model and best_model.segments_:
                        pred_slopes = [seg['slope'] for seg in best_model.segments_]

                elif m_type == 'mannks_hybrid':
                    # Hybrid Segmented Trend
                    # Uses OLS for structure, MannKS for slopes
                    # It handles model selection internally via OLS BIC logic in fit()
                    # We assume max_breakpoints=2 for parity
                    model = HybridSegmentedTrend(max_breakpoints=2)
                    model.fit(t, x)

                    pred_n = model.n_breakpoints_
                    pred_bps = list(model.breakpoints_)
                    if model.segments_:
                        pred_slopes = [seg['slope'] for seg in model.segments_]

                dur = time.time() - t0

                # Store
                iter_res[f'{name}_n'] = pred_n

                # Format bps to simple list string for CSV safety
                if isinstance(pred_bps, np.ndarray):
                    bps_list = pred_bps.tolist()
                elif isinstance(pred_bps, list):
                    bps_list = pred_bps
                else:
                    bps_list = []
                iter_res[f'{name}_bps'] = str(bps_list)

                iter_res[f'{name}_time'] = dur
                iter_res[f'{name}_correct_n'] = (pred_n == true_n)

                # Location Error (if N matches)
                if pred_n == true_n and true_n > 0:
                    # Match bps
                    # Ensure pred_bps is a list of floats, handle if it's already a list or needs conversion
                    if isinstance(pred_bps, list):
                        p = np.sort(pred_bps)
                    else:
                        p = np.sort(list(pred_bps))

                    gt = np.sort(true_bps)
                    if len(p) == len(gt):
                        err = np.mean(np.abs(p - gt))
                        iter_res[f'{name}_loc_error'] = err
                    else:
                         iter_res[f'{name}_loc_error'] = np.nan
                else:
                    iter_res[f'{name}_loc_error'] = np.nan

                # Slope Error (if N matches and true_slopes provided)
                if pred_n == true_n and true_slopes is not None:
                    # Slopes should match segment by segment if sorted by time
                    # Our segments are time-sorted.
                    # true_slopes logic assumes time-sorted segments
                    if len(pred_slopes) == len(true_slopes):
                        s_err = np.mean(np.abs(np.array(pred_slopes) - np.array(true_slopes)))
                        iter_res[f'{name}_slope_error'] = s_err
                    else:
                        iter_res[f'{name}_slope_error'] = np.nan
                else:
                    iter_res[f'{name}_slope_error'] = np.nan

            except Exception as e:
                logger.error(f"Error in {name} iter {i}: {e}")
                iter_res[f'{name}_n'] = -1
                iter_res[f'{name}_time'] = time.time() - t0

        results.append(iter_res)

        # Incremental save every 10
        if i % 10 == 0:
            pd.DataFrame(results).to_csv(os.path.join(output_dir, 'results_partial.csv'), index=False)

    total_time = time.time() - start_total
    logger.info(f"Completed in {total_time:.2f}s")

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(output_dir, 'results_final.csv'), index=False)

    generate_summary_report(df, output_dir, methods)
    return df

def generate_summary_report(df, output_dir, methods):
    lines = []
    lines.append("# Validation Report\n")

    # 1. Accuracy of N
    lines.append("## 1. Model Selection Accuracy (Correct N)\n")
    lines.append("| Method | Accuracy | Mean Time (s) |\n")
    lines.append("| :--- | :--- | :--- |\n")

    for name, _, _ in methods:
        acc = df[f'{name}_correct_n'].mean()
        tm = df[f'{name}_time'].mean()
        lines.append(f"| {name} | {acc:.1%} | {tm:.4f} |\n")

    # 2. Location Accuracy
    lines.append("\n## 2. Breakpoint Location Accuracy (MAE)\n")
    lines.append("| Method | Mean Error | Std Dev | Min | Max |\n")
    lines.append("| :--- | :--- | :--- | :--- | :--- |\n")

    for name, _, _ in methods:
        # Filter for correct detections
        errs = df[f'{name}_loc_error'].dropna()
        if len(errs) > 0:
            mean_e = errs.mean()
            std_e = errs.std()
            min_e = errs.min()
            max_e = errs.max()
            lines.append(f"| {name} | {mean_e:.4f} | {std_e:.4f} | {min_e:.4f} | {max_e:.4f} |\n")
        else:
            lines.append(f"| {name} | N/A | N/A | N/A | N/A |\n")

    # 3. Slope Estimation Accuracy (MAE)
    lines.append("\n## 3. Slope Estimation Accuracy (MAE)\n")
    lines.append("| Method | Mean Error | Std Dev | Min | Max |\n")
    lines.append("| :--- | :--- | :--- | :--- | :--- |\n")

    for name, _, _ in methods:
        col = f'{name}_slope_error'
        if col in df.columns:
            errs = df[col].dropna()
            if len(errs) > 0:
                mean_e = errs.mean()
                std_e = errs.std()
                min_e = errs.min()
                max_e = errs.max()
                lines.append(f"| {name} | {mean_e:.4f} | {std_e:.4f} | {min_e:.4f} | {max_e:.4f} |\n")
            else:
                lines.append(f"| {name} | N/A | N/A | N/A | N/A |\n")
        else:
            lines.append(f"| {name} | N/A | N/A | N/A | N/A |\n")

    # 4. Contingency Tables (Confusion Matrix)
    lines.append("\n## 3. Confusion Matrix (True N vs Predicted N)\n")

    for name, _, _ in methods:
        lines.append(f"\n### {name}\n")
        if 'true_n' in df.columns and f'{name}_n' in df.columns:
            # Create crosstab
            ct = pd.crosstab(df['true_n'], df[f'{name}_n'])
            ct.index.name = "True N"
            ct.columns.name = "Pred N"

            # Convert to markdown manually or via to_markdown if available
            try:
                # Use simple formatting
                header = "| True N \\ Pred N | " + " | ".join(map(str, ct.columns)) + " |"
                sep = "| :--- | " + " | ".join(["---"] * len(ct.columns)) + " |"
                lines.append(header + "\n")
                lines.append(sep + "\n")

                for idx, row in ct.iterrows():
                    row_str = " | ".join(map(str, row.values))
                    lines.append(f"| **{idx}** | {row_str} |\n")
            except Exception as e:
                lines.append(f"Error generating table: {e}\n")
        else:
            lines.append("Data not available for contingency table.\n")

    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.writelines(lines)
