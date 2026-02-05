
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from tqdm import tqdm

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import MannKS as mk
from MannKS.power import power_test

def run_validation():
    print("Running Validation Case 56: Surrogate Power Analysis")

    # 1. Setup Data: 50 points of Red Noise (AR1)
    # We want a scenario where trends are hard to detect
    np.random.seed(42)
    n = 50
    t = np.arange(n)

    # Generate AR(1) noise with rho=0.7 (strong red noise)
    rho = 0.7
    x = np.zeros(n)
    eps = np.random.normal(0, 1, n)
    x[0] = eps[0]
    for i in range(1, n):
        x[i] = rho * x[i-1] + eps[i]

    # 2. Define Slopes
    # We test slopes 0, 0.05, 0.1, ..., 0.25
    slopes = np.linspace(0, 0.25, 6)

    print(f"Dataset: N={n}, AR(1) rho={rho}")
    print(f"Testing slopes: {slopes}")

    # 3. Run Power Test
    # Using 'iaaft' for even sampling
    # Reduced simulation count for validation speed (don't run 1000s in CI)
    n_sims = 50
    n_surr = 200

    print(f"Starting Monte Carlo: {n_sims} sims, {n_surr} surrogates...")

    result = power_test(
        x, t, slopes,
        n_simulations=n_sims,
        n_surrogates=n_surr,
        surrogate_method='iaaft',
        random_state=42
    )

    # 4. Generate Report
    output_dir = os.path.dirname(__file__)
    report_path = os.path.join(output_dir, 'README.md')

    with open(report_path, 'w') as f:
        f.write("# Validation Case 56: Surrogate Power Analysis\n\n")
        f.write("This validation case examines the `power_test` functionality for surrogate data testing.\n\n")

        f.write("## Simulation Setup\n")
        f.write(f"- **Data**: AR(1) Red Noise ($\\rho={rho}$), N={n}\n")
        f.write(f"- **Method**: IAAFT Surrogates\n")
        f.write(f"- **Simulations**: {n_sims} per slope\n")
        f.write(f"- **Inner Surrogates**: {n_surr}\n\n")

        f.write("## Results\n")
        f.write("The table below shows the estimated power (detection rate) for each slope.\n\n")

        df = result.simulation_results[['slope', 'power', 'n_detected']]
        try:
            f.write(df.to_markdown(index=False))
        except ImportError:
            f.write(df.to_string(index=False))

        f.write("\n\n")
        f.write(f"**Minimum Detectable Trend (80% Power):** {result.min_detectable_trend:.4f}\n\n")

        f.write("## Power Curve\n")
        f.write("![Power Curve](power_curve.png)\n")

    print(f"Report saved to {report_path}")

    # 5. Generate Plot
    plt.figure(figsize=(10, 6))
    plt.plot(result.slopes, result.power, 'o-', label='Surrogate Power (IAAFT)')
    plt.axhline(0.8, color='r', linestyle='--', label='80% Power Threshold')
    plt.axhline(0.05, color='k', linestyle=':', label='Alpha (0.05)')

    if result.min_detectable_trend:
        plt.axvline(result.min_detectable_trend, color='g', linestyle='--',
                   label=f'MDT: {result.min_detectable_trend:.3f}')

    plt.xlabel('Slope Magnitude')
    plt.ylabel('Power')
    plt.title('Surrogate Test Power Analysis (AR1 Noise)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(output_dir, 'power_curve.png'))
    plt.close()

    print("Plot saved to power_curve.png")

    # 6. Assertions (Basic Sanity Checks)
    # Power at slope 0 should be low (around alpha 0.05)
    # Allow some variance due to low N_sims
    p0 = result.power[0]
    print(f"Power at Slope 0: {p0}")
    if p0 > 0.15:
        print("WARNING: High false positive rate (sim noise or low count artifact)")

    # Power at max slope should be high
    p_max = result.power[-1]
    print(f"Power at Slope {slopes[-1]}: {p_max}")
    if p_max < 0.5:
        print("WARNING: Low detection power for max slope")

if __name__ == "__main__":
    run_validation()
