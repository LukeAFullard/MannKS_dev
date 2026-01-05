import os
import numpy as np
import pandas as pd
import piecewise_regression
import MannKS as mk
from MannKS.segmented_trend_test import find_best_segmentation
import matplotlib.pyplot as plt
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(OUTPUT_DIR, 'README.md')
RESULTS_FILE = os.path.join(OUTPUT_DIR, 'comparison_results.csv')

def generate_random_dataset(n_points=100, seed=None):
    if seed is not None:
        np.random.seed(seed)

    t = np.linspace(0, 100, n_points)

    # Decide number of breakpoints (0, 1, or 2)
    n_bp = np.random.choice([0, 1, 2], p=[0.2, 0.4, 0.4])

    # Base params
    intercept = 10
    slopes = [np.random.uniform(-0.5, 0.5)]

    # Generate breakpoints
    bps = []
    if n_bp > 0:
        # Pick random points in range [20, 80] ensuring separation
        bp1 = np.random.uniform(20, 80)
        bps.append(bp1)
        if n_bp > 1:
            # Ensure 2nd bp is far enough
            min_dist = 20
            low = bp1 + min_dist
            if low < 90:
                bp2 = np.random.uniform(low, 90)
                bps.append(bp2)
            else:
                # Fallback to 1 bp if squeezed
                n_bp = 1
                bps = [bp1]

    # Generate slopes
    for _ in range(n_bp):
        # Change slope significantly to make it detectable
        prev_slope = slopes[-1]
        # New slope should differ by at least 0.1
        delta = np.random.uniform(0.1, 0.5) * np.random.choice([-1, 1])
        slopes.append(prev_slope + delta)

    # Generate y
    y = np.zeros_like(t)

    # Segment 0
    if n_bp == 0:
        y = intercept + slopes[0] * t
    elif n_bp == 1:
        mask1 = t < bps[0]
        y[mask1] = intercept + slopes[0] * t[mask1]

        y_at_bp1 = intercept + slopes[0] * bps[0]
        y[~mask1] = y_at_bp1 + slopes[1] * (t[~mask1] - bps[0])
    elif n_bp == 2:
        mask1 = t < bps[0]
        mask2 = (t >= bps[0]) & (t < bps[1])
        mask3 = t >= bps[1]

        y[mask1] = intercept + slopes[0] * t[mask1]

        y_at_bp1 = intercept + slopes[0] * bps[0]
        y[mask2] = y_at_bp1 + slopes[1] * (t[mask2] - bps[0])

        y_at_bp2 = y_at_bp1 + slopes[1] * (bps[1] - bps[0])
        y[mask3] = y_at_bp2 + slopes[2] * (t[mask3] - bps[1])

    # Add noise
    # Signal magnitude over 100 steps is ~ 0.5 * 100 = 50.
    # Medium SNR: Sigma = 2.0.
    noise = np.random.normal(0, 2.0, n_points)
    y += noise

    return t, y, n_bp, bps

def run_comparison(n_iterations=50):
    results = []

    print(f"Running {n_iterations} comparison iterations (Medium SNR, Sigma=2.0)...")

    for i in range(n_iterations):
        if i % 10 == 0:
            print(f"Iteration {i}/{n_iterations}...")

        t, x, true_n, true_bps = generate_random_dataset(seed=42+i)

        # -----------------------------------
        # 1. Piecewise Regression (Standard OLS)
        # -----------------------------------
        try:
            ms_pw = piecewise_regression.ModelSelection(t, x, max_breakpoints=2)
            # Find best model based on BIC
            best_bic_pw = np.inf
            best_model_pw = None

            for fit in ms_pw.models:
                res = fit.get_results()
                bic = res.get('bic')
                if bic is not None and bic < best_bic_pw:
                    best_bic_pw = bic
                    best_model_pw = fit

            pw_n = best_model_pw.n_breakpoints
            if pw_n > 0:
                est = best_model_pw.get_results()['estimates']
                pw_bps = []
                for k in range(1, pw_n + 1):
                    pw_bps.append(est[f'breakpoint{k}']['estimate'])
            else:
                pw_bps = []

        except Exception as e:
            # print(f"Piecewise Regression failed on iter {i}: {e}")
            pw_n = -1
            pw_bps = []

        # -----------------------------------
        # 2. MannKS - Standard (merge=False)
        # -----------------------------------
        try:
            mk_res, _ = find_best_segmentation(
                x=x, t=t, max_breakpoints=2, n_bootstrap=20, alpha=0.05,
                min_segment_size=3, merge_similar_segments=False
            )
            mk_n = mk_res.n_breakpoints
            mk_bps = list(mk_res.breakpoints)
        except Exception as e:
            mk_n = -1
            mk_bps = []

        # -----------------------------------
        # 3. MannKS - Merged (merge=True)
        # -----------------------------------
        try:
            mk_merge_res, _ = find_best_segmentation(
                x=x, t=t, max_breakpoints=2, n_bootstrap=20, alpha=0.05,
                min_segment_size=3, merge_similar_segments=True
            )
            mk_merge_n = mk_merge_res.n_breakpoints
            mk_merge_bps = list(mk_merge_res.breakpoints)
        except Exception as e:
            mk_merge_n = -1
            mk_merge_bps = []

        # -----------------------------------
        # Calculate Error Metrics
        # -----------------------------------
        row = {
            'iter': i,
            'true_n': true_n,
            'true_bps': str(true_bps),
            'pw_n': pw_n,
            'mk_n': mk_n,
            'mk_merge_n': mk_merge_n,
            'pw_bps': str(pw_bps),
            'mk_bps': str(mk_bps),
            'mk_merge_bps': str(mk_merge_bps),

            # Correct N Detection
            'pw_correct_n': (pw_n == true_n),
            'mk_correct_n': (mk_n == true_n),
            'mk_merge_correct_n': (mk_merge_n == true_n)
        }

        # Calculate Breakpoint Location Error (only if N matches true N and N > 0)
        def calc_bp_error(pred_bps, true_bps):
            if len(pred_bps) != len(true_bps):
                return np.nan
            if len(true_bps) == 0:
                return 0.0 # No error if no breakpoints
            # Sort both
            p = np.sort(pred_bps)
            t = np.sort(true_bps)
            return np.mean(np.abs(p - t))

        if pw_n == true_n:
            row['pw_loc_error'] = calc_bp_error(pw_bps, true_bps)
        else:
            row['pw_loc_error'] = np.nan

        if mk_n == true_n:
            row['mk_loc_error'] = calc_bp_error(mk_bps, true_bps)
        else:
            row['mk_loc_error'] = np.nan

        if mk_merge_n == true_n:
            row['mk_merge_loc_error'] = calc_bp_error(mk_merge_bps, true_bps)
        else:
            row['mk_merge_loc_error'] = np.nan

        results.append(row)

    df_res = pd.DataFrame(results)
    df_res.to_csv(RESULTS_FILE, index=False)
    return df_res

def generate_report(df):
    total = len(df)

    # Accuracy Rates
    pw_acc = df['pw_correct_n'].mean()
    mk_acc = df['mk_correct_n'].mean()
    mk_merge_acc = df['mk_merge_correct_n'].mean()

    # Location Errors (Filter out NaN)
    pw_err = df['pw_loc_error'].mean()
    mk_err = df['mk_loc_error'].mean()
    mk_merge_err = df['mk_merge_loc_error'].mean()

    # Confusion Matrices
    cm_pw = pd.crosstab(df['true_n'], df['pw_n'])
    cm_mk = pd.crosstab(df['true_n'], df['mk_n'])
    cm_mk_merge = pd.crosstab(df['true_n'], df['mk_merge_n'])

    with open(REPORT_FILE, 'w') as f:
        f.write("# Validation 51: Medium SNR Breakpoint Detection\n\n")
        f.write(f"Comparision across {total} random datasets (Non-censored, Medium SNR, Sigma=2.0) against **Ground Truth**.\n\n")

        f.write("## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)\n")
        f.write("| Method | Accuracy (Correct N) |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| Piecewise (OLS) | {pw_acc:.1%} |\n")
        f.write(f"| MannKS (Standard) | {mk_acc:.1%} |\n")
        f.write(f"| **MannKS (Merged)** | **{mk_merge_acc:.1%}** |\n\n")

        f.write("### Confusion Matrices (Rows=True N, Cols=Predicted N)\n")
        f.write("#### Piecewise (OLS)\n")
        f.write(cm_pw.to_markdown())
        f.write("\n\n")
        f.write("#### MannKS (Standard)\n")
        f.write(cm_mk.to_markdown())
        f.write("\n\n")
        f.write("#### MannKS (Merged)\n")
        f.write(cm_mk_merge.to_markdown())
        f.write("\n\n")

        f.write("## 2. Breakpoint Location Accuracy\n")
        f.write("Mean Absolute Error (MAE) when the correct number of breakpoints was found.\n\n")
        f.write("| Method | Mean Location Error |\n")
        f.write("| :--- | :--- |\n")
        f.write(f"| Piecewise (OLS) | {pw_err:.4f} |\n")
        f.write(f"| MannKS (Standard) | {mk_err:.4f} |\n")
        f.write(f"| MannKS (Merged) | {mk_merge_err:.4f} |\n\n")

        f.write("## 3. Analysis\n")
        f.write("*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments (specifically reducing over-segmentation)?\n")
        if mk_merge_acc > mk_acc:
             f.write("    *   **Yes.** The merging step improved overall accuracy, likely by correcting cases where standard BIC overestimated the number of breakpoints.\n")
        elif mk_merge_acc < mk_acc:
             f.write("    *   **No.** The merging step reduced accuracy, possibly by under-segmenting (merging distinct segments incorrectly).\n")
        else:
             f.write("    *   **Neutral.** Performance was identical.\n")

        f.write("*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?\n")
        f.write(f"    *   MannKS (Merged) is within {abs(pw_acc - mk_merge_acc)*100:.1f}% accuracy of OLS.\n")

if __name__ == "__main__":
    df = run_comparison(n_iterations=200)
    generate_report(df)
    print("Comparison complete.")
