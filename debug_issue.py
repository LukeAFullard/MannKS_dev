
import MannKS._stats as stats
import numpy as np

# Test case where Z is exactly zero
z = 0.0
alpha = 0.05
continuous = True

p, h, trend = stats._p_value(z, alpha, continuous)
print(f"Z={z}, Trend={trend}")

# Test case where Z is very close to zero but not zero
z_small = 1e-15
p_small, h_small, trend_small = stats._p_value(z_small, alpha, continuous)
print(f"Z={z_small}, Trend={trend_small}")
