
import numpy as np
import pandas as pd
from MannKS import segmented_trend_test

# Generate simple segmented data
t = np.linspace(0, 100, 100)
x = np.zeros_like(t)
x[t < 50] = t[t < 50]
x[t >= 50] = 50 - 0.5 * (t[t >= 50] - 50)
x += np.random.normal(0, 0.5, size=len(t))

# Run with use_bagging=False (default)
# Force 1 breakpoint to ensure we get a result with breakpoints
result = segmented_trend_test(x, t, n_breakpoints=1, use_bagging=False)

print(f"Breakpoints: {result.breakpoints}")
print(f"Breakpoint CIs: {result.breakpoint_cis}")

# Check if CIs are valid (not all NaNs)
cis = result.breakpoint_cis
if len(cis) > 0 and not np.isnan(cis[0][0]):
    print("VERIFICATION SUCCESS: CIs are present without bagging.")
else:
    print("VERIFICATION FAILED: CIs are missing or NaN.")
