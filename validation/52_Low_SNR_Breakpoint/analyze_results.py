
import pandas as pd
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(OUTPUT_DIR, 'results_final.csv')
README_PATH = os.path.join(OUTPUT_DIR, 'README.md')

def analyze():
    if not os.path.exists(CSV_PATH):
        print("Error: results_final.csv not found.")
        return

    df = pd.read_csv(CSV_PATH)

    methods = [
        'OLS_Piecewise',
        'MannKS_BIC',
        'MannKS_mBIC',
        'MannKS_AIC',
        'MannKS_AIC_Merge',
        'MannKS_AIC_Bagging'
    ]

    # --- 1. Breakdown by True N ---
    print("\n## 3. Breakdown by True Breakpoint Count (N)")

    for n in sorted(df['true_n'].unique()):
        print(f"\n### True N = {n}")
        subset = df[df['true_n'] == n]
        count = len(subset)
        print(f"(Sample Size: {count})")

        print("| Method | Selection Accuracy | Loc MAE (Correct N only) |")
        print("| :--- | :--- | :--- |")

        for method in methods:
            # Accuracy
            correct_col = f'{method}_correct_n'
            acc = subset[correct_col].mean()

            # Location MAE (only where N was correct)
            # Filter subset where this method got it right
            correct_subset = subset[subset[correct_col] == True]
            if n > 0 and len(correct_subset) > 0:
                mae = correct_subset[f'{method}_loc_error'].mean()
                mae_str = f"{mae:.4f}"
            elif n == 0:
                mae_str = "N/A"
            else:
                mae_str = "No Correct Hits"

            print(f"| {method} | {acc:.1%} | {mae_str} |")

    # --- 2. Confusion Matrix Analysis (Optional, helpful for debugging) ---
    # Not printing to MD, just for our insight
    # print("\n--- Debug: Confusion Matrices ---")
    # for method in methods:
    #     print(f"\n{method}:")
    #     print(pd.crosstab(df['true_n'], df[f'{method}_n']))

if __name__ == "__main__":
    analyze()
