# Validation Report


    # V-09: Right-Censored Trend

    This validation case tests the package's ability to handle right-censored data (values reported as greater than a detection limit, e.g., `>5.0`).

    Three scenarios were tested:
    1. **Strong Increasing Trend**: Data with a clear positive slope, where higher values are censored.
    2. **Weak Decreasing Trend**: Data with a slight negative slope, where initial high values are censored.
    3. **Stable (No Trend)**: Random data with no trend, with some high values censored.


## Plots
### v09_combined.png
![v09_combined.png](v09_combined.png)

### v09_strong_right_censored.png
![v09_strong_right_censored.png](v09_strong_right_censored.png)

## Results
               Test ID                Method     Slope      P-Value  Lower CI  Upper CI
V-09_strong_increasing MannKenSen (Standard)  1.904815 3.004074e-04  1.514761  2.306317
V-09_strong_increasing MannKenSen (LWP Mode)  1.847925 5.551291e-09  1.455149  2.239489
V-09_strong_increasing        LWP-TRENDS (R)  1.847925 4.802735e-09  1.513655  2.189103
V-09_strong_increasing      MannKenSen (ATS)  1.709259 3.004074e-04  1.408599  2.024888
V-09_strong_increasing             NADA2 (R)  1.281998 2.851641e-04       NaN       NaN
  V-09_weak_decreasing MannKenSen (Standard) -0.025660 7.183023e-01 -0.698598  0.678248
  V-09_weak_decreasing MannKenSen (LWP Mode)  0.000000 9.565499e-01 -0.674868  0.640895
  V-09_weak_decreasing        LWP-TRENDS (R)  0.000000 9.564354e-01 -0.485501  0.509951
  V-09_weak_decreasing      MannKenSen (ATS) -0.025660 7.183023e-01 -0.576307  0.505012
  V-09_weak_decreasing             NADA2 (R) -0.124127 7.176947e-01       NaN       NaN
           V-09_stable MannKenSen (Standard) -0.047120 5.972643e-01 -0.456799  0.301222
           V-09_stable MannKenSen (LWP Mode)  0.000000 8.487665e-01 -0.400623  0.259358
           V-09_stable        LWP-TRENDS (R)  0.000000 8.481483e-01 -0.332156  0.182018
           V-09_stable      MannKenSen (ATS) -0.027932 5.972643e-01 -0.307415  0.241216
           V-09_stable             NADA2 (R)  0.065367 5.958990e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-09_strong_increasing 2.220446e-16   1.110223e-14
  V-09_weak_decreasing 0.000000e+00  -0.000000e+00
           V-09_stable 0.000000e+00   0.000000e+00
