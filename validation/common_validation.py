
import os
import sys
import numpy as np
import pandas as pd
import time
import logging
import warnings
from scipy.optimize import minimize
from MannKS.segmented_trend_test import find_best_segmentation

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

# --- 1. OLS Piecewise Implementation (Baseline) ---
# Simple implementation since no external lib installed
def fit_piecewise_ols(t, y, max_breakpoints=2):
    """
    Fits piecewise linear regression using OLS (via scipy.optimize)
    Searches for 0, 1, ..., max_breakpoints and selects best via BIC.
    Assumes continuous model.
    """
    n = len(y)
    best_bic = np.inf
    best_n = 0
    best_bps = []

    # 0 Breakpoints (Linear)
    # y = a + b*t
    A = np.vstack([t, np.ones(n)]).T
    try:
        sol, resid, _, _ = np.linalg.lstsq(A, y, rcond=None)
        if resid.size > 0:
            ssr = resid[0]
        else:
            # Perfect fit or calculation
            y_pred = sol[0]*t + sol[1]
            ssr = np.sum((y - y_pred)**2)

        k = 2 # slope, intercept
        if ssr <= 1e-10: ssr = 1e-10
        bic = n * np.log(ssr/n) + k * np.log(n)

        if bic < best_bic:
            best_bic = bic
            best_n = 0
            best_bps = []
    except:
        pass

    # 1 Breakpoint
    if max_breakpoints >= 1:
        def objective_1bp(params):
            bp = params[0]
            if bp <= t.min() or bp >= t.max(): return 1e20 # Constraint
            # Construct features
            # Continuous: y = a + b1*t + b2*max(0, t-bp)
            # This forces continuity at bp.
            # b1 is slope1. b2 is change in slope.

            term2 = np.maximum(0, t - bp)
            A = np.vstack([t, term2, np.ones(n)]).T
            sol, resid, _, _ = np.linalg.lstsq(A, y, rcond=None)
            if resid.size > 0: return resid[0]
            y_pred = np.dot(A, sol)
            return np.sum((y-y_pred)**2)

        # Optimize breakpoint location
        # Grid search initialization + minimization
        t_min, t_max = t.min(), t.max()
        grid = np.linspace(t_min + (t_max-t_min)*0.1, t_max - (t_max-t_min)*0.1, 5)

        local_best_ssr = np.inf
        local_best_bp = None

        for start_bp in grid:
            res = minimize(objective_1bp, [start_bp], bounds=[(t_min, t_max)], method='L-BFGS-B')
            if res.fun < local_best_ssr:
                local_best_ssr = res.fun
                local_best_bp = res.x[0]

        # BIC
        # k = 4 (intercept, slope1, slope_change, breakpoint)
        k = 4
        if local_best_ssr <= 1e-10: local_best_ssr = 1e-10
        bic = n * np.log(local_best_ssr/n) + k * np.log(n)

        if bic < best_bic:
            best_bic = bic
            best_n = 1
            best_bps = [local_best_bp]

    # 2 Breakpoints
    if max_breakpoints >= 2:
        def objective_2bp(params):
            bp1, bp2 = sorted(params)
            if bp1 <= t.min() or bp2 >= t.max() or bp2 <= bp1 + 1e-5: return 1e20

            # y = a + b1*t + b2*max(0, t-bp1) + b3*max(0, t-bp2)
            term2 = np.maximum(0, t - bp1)
            term3 = np.maximum(0, t - bp2)
            A = np.vstack([t, term2, term3, np.ones(n)]).T
            sol, resid, _, _ = np.linalg.lstsq(A, y, rcond=None)
            if resid.size > 0: return resid[0]
            y_pred = np.dot(A, sol)
            return np.sum((y-y_pred)**2)

        grid_start = np.linspace(t_min + (t_max-t_min)*0.1, t_max - (t_max-t_min)*0.1, 4)
        local_best_ssr = np.inf
        local_best_bps = None

        for s1 in grid_start:
            for s2 in grid_start:
                if s2 > s1 + (t_max-t_min)*0.1:
                    res = minimize(objective_2bp, [s1, s2], bounds=[(t_min, t_max), (t_min, t_max)], method='L-BFGS-B')
                    if res.fun < local_best_ssr:
                        local_best_ssr = res.fun
                        local_best_bps = sorted(res.x)

        # BIC
        # k = 6 (int, s1, ds2, ds3, bp1, bp2)
        k = 6
        if local_best_ssr <= 1e-10: local_best_ssr = 1e-10
        bic = n * np.log(local_best_ssr/n) + k * np.log(n)

        if bic < best_bic:
            best_bic = bic
            best_n = 2
            best_bps = local_best_bps

    return best_n, best_bps

# --- 2. Generic Run Function ---
def run_validation_suite(data_generator, output_dir, n_iterations=100):
    logger = setup_logging(output_dir)
    logger.info(f"Starting validation suite with {n_iterations} iterations.")

    results = []

    # Define methods
    methods = [
        ('OLS_Piecewise', 'ols', {}),
        ('MannKS_BIC', 'mannks', {'criterion': 'bic'}),
        ('MannKS_mBIC', 'mannks', {'criterion': 'mbic'}),
        ('MannKS_AIC', 'mannks', {'criterion': 'aic'}),
        ('MannKS_AIC_Merge', 'mannks', {'criterion': 'aic', 'merge_similar_segments': True}),
        ('MannKS_AIC_Bagging', 'mannks', {'criterion': 'aic', 'use_bagging': True})
    ]

    start_total = time.time()

    for i in range(n_iterations):
        t, x, true_n, true_bps = data_generator(seed=42+i)

        iter_res = {
            'iter': i,
            'true_n': true_n,
            'true_bps': str(list(true_bps))
        }

        if i % 10 == 0:
            logger.info(f"Processing iteration {i}/{n_iterations}...")

        for name, m_type, kwargs in methods:
            t0 = time.time()
            try:
                if m_type == 'ols':
                    pred_n, pred_bps = fit_piecewise_ols(t, x, max_breakpoints=2)
                else:
                    # MannKS
                    # Use common robust defaults
                    res, _ = find_best_segmentation(
                        x=x, t=t,
                        max_breakpoints=2,
                        n_bootstrap=50, # Fast but robust enough for location
                        alpha=0.05,
                        min_segment_size=5,
                        normalize_time=True, # Use new feature for stability
                        continuity=True, # Default behavior usually expected unless jumps
                        **kwargs
                    )
                    pred_n = res.n_breakpoints
                    pred_bps = list(res.breakpoints)

                dur = time.time() - t0

                # Store
                iter_res[f'{name}_n'] = pred_n
                iter_res[f'{name}_bps'] = str(pred_bps)
                iter_res[f'{name}_time'] = dur
                iter_res[f'{name}_correct_n'] = (pred_n == true_n)

                # Location Error (if N matches)
                if pred_n == true_n and true_n > 0:
                    # Match bps
                    p = np.sort(pred_bps)
                    gt = np.sort(true_bps)
                    err = np.mean(np.abs(p - gt))
                    iter_res[f'{name}_loc_error'] = err
                else:
                    iter_res[f'{name}_loc_error'] = np.nan

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

    with open(os.path.join(output_dir, 'README.md'), 'w') as f:
        f.writelines(lines)
