
import os
import sys
import numpy as np

# Add parent dir to sys.path to import common_validation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common_validation import run_validation_suite

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_data(seed=None):
    if seed is not None:
        np.random.seed(seed)

    n_points = 100
    t = np.linspace(0, 100, n_points)

    n_bp = np.random.choice([0, 1, 2], p=[0.2, 0.4, 0.4])

    bps = []
    if n_bp == 1:
        bps = [np.random.uniform(25, 75)]
    elif n_bp == 2:
        b1 = np.random.uniform(20, 60)
        b2 = np.random.uniform(b1 + 20, 90)
        bps = [b1, b2]

    slopes = [np.random.uniform(-0.5, 0.5)]
    for _ in range(n_bp):
        # Low SNR: Very small changes
        delta = np.random.uniform(0.05, 0.15) * np.random.choice([-1, 1])
        slopes.append(slopes[-1] + delta)

    y = np.zeros_like(t)
    y = 10 + slopes[0] * t

    for i, bp in enumerate(bps):
        mask = t >= bp
        delta = slopes[i+1] - slopes[i]
        y[mask] += delta * (t[mask] - bp)

    # Noise: Same 1.0. Signal is now very weak.
    y += np.random.normal(0, 1.0, n_points)

    return t, y, n_bp, bps

if __name__ == "__main__":
    print("Script setup complete. Running validation...")
    run_validation_suite(generate_data, OUTPUT_DIR, n_iterations=50)
