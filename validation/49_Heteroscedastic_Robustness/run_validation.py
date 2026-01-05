import os
import numpy as np
import pandas as pd
import piecewise_regression
import MannKS as mk
from MannKS.segmented_trend_test import find_best_segmentation
import matplotlib.pyplot as plt
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(OUTPUT_DIR, 'README.md')
RESULTS_FILE = os.path.join(OUTPUT_DIR, 'robustness_results.csv')

def generate_robust_dataset(n_points=100, seed=None):
    if seed is not None:
        np.random.seed(seed)

    t = np.linspace(0, 100, n_points)

    # 1. Base Structure (Always 1 Breakpoint)
    bp_true = np.random.uniform(40, 60)

    # Slopes: Change from 0.5 to 1.5 (Kink)
    slope1 = 0.5
    slope2 = 1.5
    intercept = 10

    y = np.zeros_like(t)
    mask = t < bp_true
    y[mask] = intercept + slope1 * t[mask]
    y[~mask] = (intercept + slope1 * bp_true) + slope2 * (t[~mask] - bp_true)

    # 2. Add Noise: Heteroscedastic
    # Variance increases with time
    # Sigma grows from 0.5 to 3.0
    sigma = np.linspace(0.5, 3.0, n_points)
    noise = np.random.normal(0, sigma, n_points)
    y += noise

    return t, y, bp_true

def run_comparison(n_iterations=200):
    results = []
    print(f"Running Heteroscedastic Robustness Test ({n_iterations} iterations)...")

    for i in range(n_iterations):
        if i % 20 == 0:
            print(f"  Iteration {i}/{n_iterations}")

        seed = 42 + i
        t, x, true_bp = generate_robust_dataset(n_points=60, seed=seed)

        # 1. Piecewise (OLS)
        try:
            ms_pw = piecewise_regression.ModelSelection(t, x, max_breakpoints=2)
            summaries = ms_pw.model_summaries
            if summaries:
                best_summary = min(summaries, key=lambda x: x['bic'])
                pw_n = best_summary['n_breakpoints']

                if pw_n == 1:
                    found_fit = False
                    for fit in ms_pw.models:
                        if fit.n_breakpoints == pw_n:
                            pw_bp = fit.get_results()['estimates']['breakpoint1']['estimate']
                            found_fit = True
                            break
                    if not found_fit:
                         pw_bp = np.nan
                else:
                    pw_bp = np.nan
            else:
                pw_n = -1
                pw_bp = np.nan
        except:
            pw_n = -1
            pw_bp = np.nan

        # 2. MannKS (Standard)
        try:
            mk_res, _ = find_best_segmentation(x, t, max_breakpoints=2, n_bootstrap=0, merge_similar_segments=False)
            mk_n = mk_res.n_breakpoints
            if mk_n == 1:
                mk_bp = mk_res.breakpoints[0]
            else:
                mk_bp = np.nan
        except:
            mk_n = -1
            mk_bp = np.nan

        # 3. MannKS (Merged)
        try:
            mk_m_res, _ = find_best_segmentation(x, t, max_breakpoints=2, n_bootstrap=20, merge_similar_segments=True)
            mk_m_n = mk_m_res.n_breakpoints
            if mk_m_n == 1:
                mk_m_bp = mk_m_res.breakpoints[0]
            else:
                mk_m_bp = np.nan
        except:
            mk_m_n = -1
            mk_m_bp = np.nan

        # Metrics
        row = {
            'iter': i,
            'true_bp': true_bp,

            'pw_n': pw_n,
            'mk_n': mk_n,
            'mk_m_n': mk_m_n,

            'pw_success': (pw_n == 1),
            'mk_success': (mk_n == 1),
            'mk_m_success': (mk_m_n == 1),

            'pw_error': abs(pw_bp - true_bp) if pw_n == 1 else np.nan,
            'mk_error': abs(mk_bp - true_bp) if mk_n == 1 else np.nan,
            'mk_m_error': abs(mk_m_bp - true_bp) if mk_m_n == 1 else np.nan
        }
        results.append(row)

    return pd.DataFrame(results)

def generate_report(df):
    with open(REPORT_FILE, 'w') as f:
        f.write("# Validation 49: Heteroscedastic Robustness\n\n")
        f.write("Comparison of Piecewise (OLS) vs. MannKS (Robust) under **Heteroscedastic** noise conditions (increasing variance).\n")
        f.write("The True Model has exactly **1 Breakpoint**.\n\n")

        # Success Rate (Finding exactly 1 BP)
        pw_acc = df['pw_success'].mean()
        mk_acc = df['mk_success'].mean()
        mk_m_acc = df['mk_m_success'].mean()

        f.write("## 1. Detection Accuracy (Finding 1 Breakpoint)\n")
        f.write(f"*   **Piecewise (OLS):** {pw_acc:.1%}\n")
        f.write(f"*   **MannKS (Standard):** {mk_acc:.1%}\n")
        f.write(f"*   **MannKS (Merged):** {mk_m_acc:.1%}\n\n")

        # Location Error (MAE)
        pw_err = df['pw_error'].mean()
        mk_err = df['mk_error'].mean()
        mk_m_err = df['mk_m_error'].mean()

        f.write("## 2. Location Precision (MAE)\n")
        f.write(f"*   **Piecewise (OLS):** {pw_err:.4f}\n")
        f.write(f"*   **MannKS (Standard):** {mk_err:.4f}\n")
        f.write(f"*   **MannKS (Merged):** {mk_m_err:.4f}\n\n")

        # Example Plot
        f.write("## 3. Visual Example\n")
        seed = 42
        t, y, bp = generate_robust_dataset(n_points=60, seed=seed)

        plt.figure(figsize=(10, 6))
        plt.plot(t, y, 'ko', alpha=0.6, label='Data (Heteroscedastic)')
        plt.axvline(bp, color='g', linestyle='-', alpha=0.5, label='True BP')
        plt.title("Example Data: Heteroscedasticity")
        plt.legend()
        img_name = "plot_heteroscedastic.png"
        plt.savefig(os.path.join(OUTPUT_DIR, img_name))
        plt.close()

        f.write(f"![Heteroscedastic]({img_name})\n\n")

        # Analysis
        f.write("## Analysis\n")
        if mk_acc > pw_acc or mk_err < pw_err:
            f.write("**Result:** MannKS demonstrated superior robustness in this scenario.\n\n")
        elif abs(mk_acc - pw_acc) < 0.1:
                f.write("**Result:** Both methods performed similarly.\n\n")
        else:
            f.write("**Result:** OLS remained competitive or superior.\n\n")

if __name__ == "__main__":
    df = run_comparison(n_iterations=200)
    df.to_csv(RESULTS_FILE, index=False)
    generate_report(df)
