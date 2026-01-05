import os
import numpy as np
import pandas as pd
import piecewise_regression
import MannKS as mk
from MannKS.segmented_trend_test import find_best_segmentation
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

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
    # Low SNR: Sigma = 5.0.
    noise = np.random.normal(0, 5.0, n_points)
    y += noise

    return t, y, n_bp, bps

def run_comparison(n_iterations=10):
    results = []

    print(f"Running {n_iterations} comparison iterations (Low SNR, Sigma=5.0)...")

    for i in range(n_iterations):
        t, x, true_n, true_bps = generate_random_dataset(seed=42+i)

        # -----------------------------------
        # 1. MannKS - Standard AIC (merge=False)
        # -----------------------------------
        try:
            mk_res, _ = find_best_segmentation(
                x=x, t=t, max_breakpoints=2, n_bootstrap=20, alpha=0.05,
                min_segment_size=10, merge_similar_segments=False, criterion='aic'
            )
            mk_n = mk_res.n_breakpoints
        except Exception as e:
            mk_n = -1

        # -----------------------------------
        # 2. MannKS - Improved Merging (merge=True, alpha=0.05)
        # -----------------------------------
        try:
            mk_merge_res, _ = find_best_segmentation(
                x=x, t=t, max_breakpoints=2, n_bootstrap=20, alpha=0.05,
                min_segment_size=10, merge_similar_segments=True, merging_alpha=0.05, criterion='aic'
            )
            mk_merge_n = mk_merge_res.n_breakpoints
        except Exception as e:
            mk_merge_n = -1

        # -----------------------------------
        # 3. MannKS - Permutation Test (n=100)
        # -----------------------------------
        try:
            # For permutation test, criterion doesn't matter much as we step up
            # Use small n_permutations for quick check
            mk_perm_res, _ = find_best_segmentation(
                x=x, t=t, max_breakpoints=2, n_bootstrap=20, alpha=0.05,
                min_segment_size=10, use_permutation_test=True, n_permutations=50
            )
            mk_perm_n = mk_perm_res.n_breakpoints
        except Exception as e:
            print(e)
            mk_perm_n = -1

        print(f"Iter {i}: True={true_n}, AIC={mk_n}, Merge={mk_merge_n}, Perm={mk_perm_n}")

        results.append({
            'true_n': true_n,
            'mk_n': mk_n,
            'mk_merge_n': mk_merge_n,
            'mk_perm_n': mk_perm_n
        })

    df = pd.DataFrame(results)

    # Calculate accuracy
    acc_std = (df['mk_n'] == df['true_n']).mean()
    acc_merge = (df['mk_merge_n'] == df['true_n']).mean()
    acc_perm = (df['mk_perm_n'] == df['true_n']).mean()

    print(f"\nAccuracy AIC: {acc_std:.2f}")
    print(f"Accuracy Merge: {acc_merge:.2f}")
    print(f"Accuracy Permutation: {acc_perm:.2f}")

    # Confusion Matrix
    print("\nConfusion Matrix (Permutation):")
    print(pd.crosstab(df['true_n'], df['mk_perm_n']))

if __name__ == "__main__":
    run_comparison(n_iterations=20)
