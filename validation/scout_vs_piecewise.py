import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from MannKS._scout import RobustSegmentedTrend, SimpleSegmentedTrend

def generate_synthetic_data(n=1000, n_breakpoints=1, outlier_fraction=0.05, noise_std=1.0):
    """
    Generates synthetic piecewise linear data with outliers.
    """
    X = np.sort(np.random.uniform(0, 100, n))

    # Define true breakpoints (in X space)
    bkp_locs = np.sort(np.random.uniform(20, 80, n_breakpoints))

    # Define slopes and intercepts
    # We want distinct slopes
    slopes = np.random.uniform(-2, 2, n_breakpoints + 1)

    y = np.zeros(n)
    true_segments = []

    current_x = 0
    current_y = 0

    # Create segments
    # This logic constructs a continuous function
    boundaries = np.concatenate(([0], bkp_locs, [100]))

    for i in range(len(slopes)):
        x_start = boundaries[i]
        x_end = boundaries[i+1]

        mask = (X >= x_start) & (X <= x_end)

        # y = y_start + slope * (x - x_start)
        y[mask] = current_y + slopes[i] * (X[mask] - x_start)

        # Update for next segment continuity
        current_y += slopes[i] * (x_end - x_start)

        true_segments.append({
            'slope': slopes[i],
            'x_start': x_start,
            'x_end': x_end
        })

    # Add Noise
    y_clean = y.copy()
    y += np.random.normal(0, noise_std, n)

    # Add Outliers (Spikes)
    n_outliers = int(n * outlier_fraction)
    outlier_indices = np.random.choice(n, n_outliers, replace=False)
    # Add large random values
    y[outlier_indices] += np.random.choice([-1, 1], n_outliers) * np.random.uniform(10 * noise_std, 20 * noise_std, n_outliers)

    # True breakpoint indices (approximate)
    true_bkp_indices = []
    for bp in bkp_locs:
        idx = np.argmin(np.abs(X - bp))
        true_bkp_indices.append(idx)

    return X, y, np.array(true_bkp_indices), true_segments, y_clean

def run_test_scenario(name, n=200, outlier_fraction=0.0, n_runs=5):
    print(f"\n--- Scenario: {name} (N={n}, Outliers={outlier_fraction*100}%) ---")

    robust_times = []
    robust_bkp_errs = []
    robust_slope_errs = []
    robust_mse = []

    ols_times = []
    ols_bkp_errs = []
    ols_slope_errs = []
    ols_mse = []

    for i in range(n_runs):
        X, y, true_bkps, true_segs, y_clean = generate_synthetic_data(n=n, n_breakpoints=1, outlier_fraction=outlier_fraction)

        # --- Robust Test ---
        start_time = time.time()
        robust = RobustSegmentedTrend(n_breakpoints=1)
        robust.fit(X, y)
        end_time = time.time()
        robust_times.append(end_time - start_time)

        # Prediction Test
        y_pred_robust = robust.predict(X)
        mse_robust = np.mean((y_clean - y_pred_robust)**2) # Compare to CLEAN y to verify denoising
        robust_mse.append(mse_robust)

        # Calculate Errors
        if robust.breakpoints_ is not None and len(robust.breakpoints_) > 0:
            est_bkp = robust.breakpoints_[0]
            true_bkp = true_bkps[0]
            robust_bkp_errs.append(np.abs(est_bkp - true_bkp))

            # Slope Error (Weighted Average or just first segment?)
            # Let's compare slope of first segment
            est_slope = robust.segments_[0]['slope']
            true_slope = true_segs[0]['slope']
            robust_slope_errs.append(np.abs(est_slope - true_slope))

        # --- OLS Test ---
        start_time = time.time()
        ols = SimpleSegmentedTrend(n_breakpoints=1)
        ols.fit(X, y)
        end_time = time.time()
        ols_times.append(end_time - start_time)

        y_pred_ols = ols.predict(X)
        mse_ols = np.mean((y_clean - y_pred_ols)**2)
        ols_mse.append(mse_ols)

        if ols.breakpoints_ is not None and len(ols.breakpoints_) > 0:
            est_bkp = ols.breakpoints_[0]
            true_bkp = true_bkps[0]
            ols_bkp_errs.append(np.abs(est_bkp - true_bkp))

            est_slope = ols.segments_[0]['slope']
            true_slope = true_segs[0]['slope']
            ols_slope_errs.append(np.abs(est_slope - true_slope))

    # Results
    print(f"Robust Method:")
    print(f"  Avg Time: {np.mean(robust_times):.4f}s")
    print(f"  Avg Breakpoint Index Error: {np.mean(robust_bkp_errs):.2f}")
    print(f"  Avg Slope Error: {np.mean(robust_slope_errs):.4f}")
    print(f"  Avg MSE (vs Clean Y): {np.mean(robust_mse):.4f}")

    print(f"Piecewise-Regression (OLS) Method:")
    print(f"  Avg Time: {np.mean(ols_times):.4f}s")
    print(f"  Avg Breakpoint Index Error: {np.mean(ols_bkp_errs):.2f}")
    print(f"  Avg Slope Error: {np.mean(ols_slope_errs):.4f}")
    print(f"  Avg MSE (vs Clean Y): {np.mean(ols_mse):.4f}")

    # Comparison
    print(f"Summary:")
    if np.mean(robust_slope_errs) < np.mean(ols_slope_errs):
        print("  -> Robust method is MORE ACCURATE (Slopes).")
    else:
        print("  -> OLS method is more accurate (Slopes).")

    speed_ratio = np.mean(robust_times) / np.mean(ols_times)
    print(f"  -> Robust method is {speed_ratio:.2f}x slower than OLS")

if __name__ == "__main__":
    np.random.seed(42)

    # 1. Speed Test on Large Data
    run_test_scenario("High Speed Check", n=2000, outlier_fraction=0.0, n_runs=3)

    # 2. Accuracy on Clean Data (Validation)
    run_test_scenario("Baseline Accuracy (Clean)", n=200, outlier_fraction=0.0, n_runs=5)

    # 3. Robustness on Dirty Data (The real test)
    run_test_scenario("Robustness (10% Outliers)", n=200, outlier_fraction=0.1, n_runs=5)
