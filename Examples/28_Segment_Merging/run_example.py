import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import MannKS as mk
from MannKS.segmented_trend_test import find_best_segmentation
from MannKS.plotting import plot_trend
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Setup output paths
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(OUTPUT_DIR, 'README.md')

def generate_data():
    """
    Generate data with a constant slope but a noise pattern that
    might trick BIC into seeing a breakpoint.
    """
    np.random.seed(42)
    t = np.linspace(0, 100, 80)

    # True Model: Single linear trend (Slope = 1.0)
    y = 1.0 * t

    # Add noise
    noise = np.random.normal(0, 1.0, size=len(t))

    # Add a "bump" in the middle to simulate a potential false breakpoint
    # This often tricks BIC into fitting 2 or 3 segments
    noise[30:50] += 4.0

    y += noise
    return t, y

def plot_segmentation(res, t, y, title, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(t, y, 'ko', alpha=0.5, label='Data')

    # Plot segments
    if res.segments is not None and not res.segments.empty:
        # Re-construct lines
        breakpoints = list(np.sort(res.breakpoints))
        boundaries = [np.min(t)] + breakpoints + [np.max(t)]

        for i, row in res.segments.iterrows():
            slope = row.slope
            start_t = boundaries[i]
            end_t = boundaries[i+1]

            # We need an intercept. The segment test assumes line passes through
            # (median_t, median_y_adjusted).
            # Let's approximate for visualization by filtering data in range
            mask = (t >= start_t) & (t <= end_t)
            if np.sum(mask) > 0:
                seg_t = t[mask]
                seg_y = y[mask]
                t_cent = np.median(seg_t)
                y_cent = np.median(seg_y) # Approx intercept anchor

                # Plot line segment
                line_t = np.array([start_t, end_t])
                line_y = y_cent + slope * (line_t - t_cent)

                label = f"Seg {i}: Slope={slope:.2f}" if i == 0 else None
                plt.plot(line_t, line_y, '-', linewidth=2, label=label)

                # Plot CI annotation
                mid_x = (start_t + end_t) / 2
                mid_y = y_cent + slope * (mid_x - t_cent)
                plt.text(mid_x, mid_y - 5, f"Slope CI:\n[{row.lower_ci:.2f}, {row.upper_ci:.2f}]",
                         fontsize=8, ha='center', bbox=dict(facecolor='white', alpha=0.7))

    for bp in res.breakpoints:
        plt.axvline(bp, color='r', linestyle='--', label='Breakpoint')

    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    plt.close()

def run_example():
    t, y = generate_data()

    # 1. Run Standard (No Merge)
    print("Running standard segmentation...")
    res_std, summary_std = find_best_segmentation(y, t, max_breakpoints=2, n_bootstrap=100, merge_similar_segments=False)

    # 2. Run With Merge
    print("Running segmentation with merging...")
    res_merge, summary_merge = find_best_segmentation(y, t, max_breakpoints=2, n_bootstrap=100, merge_similar_segments=True)

    # Plots
    plot_segmentation(res_std, t, y,
                     f"Before Merging: {res_std.n_breakpoints} Breakpoints Found",
                     "plot_before.png")

    plot_segmentation(res_merge, t, y,
                     f"After Merging: {res_merge.n_breakpoints} Breakpoints Found",
                     "plot_after.png")

    # Generate Report
    with open(README_PATH, 'w') as f:
        f.write("# Example 28: Merging Similar Segments\n\n")
        f.write("This example demonstrates how the `merge_similar_segments=True` option can simplify a model "
                "where the standard BIC criterion might select 'spurious' breakpoints due to noise or minor irregularities.\n\n")

        f.write("## 1. The Data\n")
        f.write("We generated synthetic data representing a single constant trend (Slope=1.0) with a noise 'bump' in the middle. "
                "This pattern often tricks statistical criteria into fitting multiple segments.\n\n")

        f.write("## 2. Before Merging (Standard BIC)\n")
        f.write(f"The standard analysis identified **{res_std.n_breakpoints}** breakpoints.\n\n")
        f.write("![Before Merging](plot_before.png)\n\n")

        if res_std.segments is not None:
            f.write("### Segment Details\n")
            f.write(res_std.segments[['slope', 'lower_ci', 'upper_ci']].to_markdown())
            f.write("\n\n")

        f.write("## 3. After Merging (Hypothesis Test)\n")
        f.write("We enabled `merge_similar_segments=True`. The algorithm checked adjacent segments. "
                "If their slope confidence intervals overlapped, they were considered indistinguishable, "
                "and the model was simplified.\n\n")

        f.write(f"The final merged model identified **{res_merge.n_breakpoints}** breakpoints.\n\n")
        f.write("![After Merging](plot_after.png)\n\n")

        if res_merge.segments is not None:
            f.write("### Segment Details\n")
            f.write(res_merge.segments[['slope', 'lower_ci', 'upper_ci']].to_markdown())
            f.write("\n\n")

        f.write("## Conclusion\n")
        if res_merge.n_breakpoints < res_std.n_breakpoints:
            f.write("The merging process successfully removed unnecessary breakpoints, simplifying the model structure.")
        else:
            f.write("The merging process retained the structure, indicating the segments were statistically distinct.")

if __name__ == "__main__":
    run_example()
