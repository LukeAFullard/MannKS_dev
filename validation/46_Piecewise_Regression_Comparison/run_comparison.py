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
    # Noise sigma = 1.0. SNR ~ 50. Good.
    noise = np.random.normal(0, 1.0, n_points)
    y += noise

    return t, y, n_bp, bps

def run_comparison(n_iterations=50):
    results = []

    print(f"Running {n_iterations} comparison iterations...")

    for i in range(n_iterations):
        if i % 5 == 0:
            print(f"Iteration {i}/{n_iterations}...")

        t, x, true_n, true_bps = generate_random_dataset(seed=42+i)

        # 1. Piecewise Regression (Standard OLS)
        try:
            # Model Selection
            ms_pw = piecewise_regression.ModelSelection(t, x, max_breakpoints=2)
            # Find best model based on BIC
            # ms_pw.models is a list of Fit objects.
            # We iterate to find min BIC
            best_bic_pw = np.inf
            best_model_pw = None

            for fit in ms_pw.models:
                # piecewise_regression Fit object has 'get_results()' dict.
                res = fit.get_results()
                bic = res.get('bic')
                if bic is not None and bic < best_bic_pw:
                    best_bic_pw = bic
                    best_model_pw = fit

            pw_n = best_model_pw.n_breakpoints
            pw_bps = best_model_pw.get_results()['estimates'].get('breakpoints', [])
            # pw_bps is a list of estimates
            if pw_n == 1:
                pw_bps = [best_model_pw.get_results()['estimates']['breakpoint1']['estimate']]
                pw_cis = [(best_model_pw.get_results()['estimates']['breakpoint1']['confidence_interval'])]
            elif pw_n == 2:
                est = best_model_pw.get_results()['estimates']
                pw_bps = [est['breakpoint1']['estimate'], est['breakpoint2']['estimate']]
                pw_cis = [est['breakpoint1']['confidence_interval'], est['breakpoint2']['confidence_interval']]
            else:
                pw_bps = []
                pw_cis = []

        except Exception as e:
            print(f"Piecewise Regression failed on iter {i}: {e}")
            pw_n = -1
            pw_bps = []
            pw_cis = []

        # 2. MannKS (Robust)
        try:
            # We use smaller n_bootstrap for speed in validation loop
            mk_res, _ = find_best_segmentation(
                x=x, t=t, max_breakpoints=2, n_bootstrap=20, alpha=0.05,
                min_segment_size=3
            )
            mk_n = mk_res.n_breakpoints
            mk_bps = mk_res.breakpoints # This might be Timestamp or float depending on input
            # Input t is float (linspace). So mk_bps is float.
            # But wait, segmented_trend_test converts numeric t to numeric internally,
            # and returns breakpoints matching input type if numeric.
            # If t is float array, is_datetime=False.
            # So mk_bps is numeric array.

            mk_bps = list(mk_bps)
            mk_cis = mk_res.breakpoint_cis

        except Exception as e:
            print(f"MannKS failed on iter {i}: {e}")
            mk_n = -1
            mk_bps = []
            mk_cis = []

        # Store result
        row = {
            'iter': i,
            'true_n': true_n,
            'true_bps': str(true_bps),
            'pw_n': pw_n,
            'mk_n': mk_n,
            'pw_bps': str(pw_bps),
            'mk_bps': str(mk_bps),
            'match_n': (pw_n == mk_n)
        }

        # Compare positions if N matches and > 0
        if pw_n == mk_n and pw_n > 0:
            # Assuming order is sorted (usually is)
            diffs = np.abs(np.array(pw_bps) - np.array(mk_bps))
            row['mean_bp_diff'] = np.mean(diffs)

            # CI widths
            pw_widths = [ci[1] - ci[0] for ci in pw_cis]
            mk_widths = [ci[1] - ci[0] for ci in mk_cis]
            row['mean_pw_ci_width'] = np.mean(pw_widths)
            row['mean_mk_ci_width'] = np.mean(mk_widths)
        else:
            row['mean_bp_diff'] = np.nan
            row['mean_pw_ci_width'] = np.nan
            row['mean_mk_ci_width'] = np.nan

        results.append(row)

    df_res = pd.DataFrame(results)
    df_res.to_csv(RESULTS_FILE, index=False)
    return df_res

def generate_report(df):
    total = len(df)

    # 1. Model Selection Agreement
    agreement_matrix = pd.crosstab(df['pw_n'], df['mk_n'])
    match_rate = df['match_n'].mean()

    # 2. Breakpoint Position Agreement
    # Filter for matches where n > 0
    valid_comparison = df[(df['match_n']) & (df['pw_n'] > 0)]
    avg_bp_diff = valid_comparison['mean_bp_diff'].mean()

    # 3. CI Width Comparison
    avg_pw_width = valid_comparison['mean_pw_ci_width'].mean()
    avg_mk_width = valid_comparison['mean_mk_ci_width'].mean()

    # New: Plot mismatches
    mismatch_df = df[~df['match_n'] & (df['pw_n'] != -1) & (df['mk_n'] != -1)]
    if not mismatch_df.empty:
        # Plot up to 2
        for i, idx in enumerate(mismatch_df.head(2).index):
            iter_id = mismatch_df.loc[idx, 'iter']
            # Re-generate data
            t, x, true_n, true_bps = generate_random_dataset(seed=42+int(iter_id))

            plt.figure(figsize=(10, 6))
            plt.scatter(t, x, color='gray', alpha=0.5, label='Data')

            # Plot PW breakpoints
            pw_bps = eval(mismatch_df.loc[idx, 'pw_bps'])
            for bp in pw_bps:
                plt.axvline(bp, color='blue', linestyle='--', label='PW Breakpoint')

            # Plot MK breakpoints
            mk_bps = eval(mismatch_df.loc[idx, 'mk_bps'])
            for bp in mk_bps:
                plt.axvline(bp, color='red', linestyle=':', label='MK Breakpoint')

            plt.title(f"Mismatch (Iter {iter_id}): PW n={mismatch_df.loc[idx, 'pw_n']}, MK n={mismatch_df.loc[idx, 'mk_n']}")

            # Dedupe legend
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = dict(zip(labels, handles))
            plt.legend(by_label.values(), by_label.keys())

            plt.savefig(os.path.join(OUTPUT_DIR, f'mismatch_plot_{i}.png'))
            plt.close()

    # Plots
    # Scatter plot of BPs
    plt.figure(figsize=(8, 8))

    # We need to extract all paired BPs
    pw_bp_list = []
    mk_bp_list = []

    for idx, row in valid_comparison.iterrows():
        # safe eval
        p = eval(row['pw_bps'])
        m = eval(row['mk_bps'])
        pw_bp_list.extend(p)
        mk_bp_list.extend(m)

    plt.scatter(pw_bp_list, mk_bp_list, alpha=0.6)
    plt.plot([0, 100], [0, 100], 'r--')
    plt.xlabel('Piecewise Regression (OLS) Breakpoint')
    plt.ylabel('MannKS (Sen) Breakpoint')
    plt.title('Comparison of Breakpoint Estimates')
    plt.savefig(os.path.join(OUTPUT_DIR, 'bp_scatter.png'))
    plt.close()

    # Markdown Report
    with open(REPORT_FILE, 'w') as f:
        f.write("# Validation 46: Comparison with `piecewise-regression`\n\n")
        f.write(f"Comparision across {total} random datasets (Non-censored, Normal noise).\n\n")

        f.write("## 1. Model Selection (Number of Breakpoints)\n")
        f.write(f"**Match Rate:** {match_rate:.1%}\n\n")
        f.write("### Confusion Matrix (Rows=Piecewise, Cols=MannKS)\n")
        f.write(agreement_matrix.to_markdown())
        f.write("\n\n")

        f.write("## 2. Breakpoint Estimation Accuracy\n")
        f.write(f"Analyzed {len(valid_comparison)} matching cases where n > 0.\n\n")
        f.write(f"**Mean Absolute Difference (MannKS vs PW):** {avg_bp_diff:.4f} units\n")
        f.write("This measures how close the robust estimator (MannKS) is to the optimal OLS estimator (PW) for normally distributed data.\n\n")
        f.write("![BP Scatter](bp_scatter.png)\n\n")

        f.write("## 3. Confidence Intervals\n")
        f.write(f"**Mean CI Width (Piecewise/OLS):** {avg_pw_width:.4f}\n")
        f.write(f"**Mean CI Width (MannKS/Bootstrap):** {avg_mk_width:.4f}\n\n")
        f.write("Note: OLS CIs assume normality and are asymptotic. MannKS CIs use percentile bootstrap. "
                "Differences are expected, but they should be of similar magnitude.\n")

if __name__ == "__main__":
    df = run_comparison(n_iterations=50)
    generate_report(df)
    print("Comparison complete.")
