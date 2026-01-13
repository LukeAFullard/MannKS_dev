
import numpy as np
import pandas as pd
from MannKS.segmented_trend_test import segmented_trend_test
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def test_config(name, n_samples, n_breakpoints=None, max_breakpoints=5):
    print(f"--- {name} (N={n_samples}, fixed_bp={n_breakpoints}, max_bp={max_breakpoints}) ---")
    t = np.arange(n_samples)
    x = t + np.random.normal(0, 0.1, n_samples) # Simple linear trend

    try:
        result = segmented_trend_test(x, t, n_breakpoints=n_breakpoints, max_breakpoints=max_breakpoints)
        print(f"Result: n_breakpoints={result.n_breakpoints}, score={result.score}")
    except Exception as e:
        print(f"FAILED: {e}")

# 1. Very small sample size
test_config("Small N=5", 5)

# 2. Fixed breakpoints too high for N
test_config("N=10, Request 5 BPs", 10, n_breakpoints=5)

# 3. Fixed breakpoints = 0
test_config("N=20, Request 0 BPs", 20, n_breakpoints=0)

# 4. Normal case
test_config("N=50, Auto", 50)
