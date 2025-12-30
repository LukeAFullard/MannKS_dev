# Validation Report


# Validation Case V-13: Censored LWP Compatibility Modes

This validation case focuses on verifying the "LWP Compatibility Mode" of the `MannKS` package against the original LWP-TRENDS R script, specifically for **right-censored** data.

The goal is to demonstrate that setting parameters `mk_test_method='lwp'` and `sens_slope_method='lwp'` allows Python to accurately replicate the R script's handling of censored values.

## Methodology
- **Data:** 4 years of monthly data (n=48).
- **Censoring:** Approximately 30% of data is **right-censored** (values above a threshold are marked as `>Threshold`).


## Plots
### v13_combined.png
![v13_combined.png](v13_combined.png)

### v13_strong.png
![v13_strong.png](v13_strong.png)

## Results
               Test ID            Method     Slope      P-Value  Lower CI  Upper CI
V-13_strong_increasing MannKS (Standard) 22.907429 2.988301e-06 21.668833 23.667608
V-13_strong_increasing MannKS (LWP Mode) 22.329999 0.000000e+00 20.815358 23.354375
V-13_strong_increasing    LWP-TRENDS (R) 22.329999 8.450761e-20 21.150546 23.186172
V-13_strong_increasing      MannKS (ATS) 23.816761 2.988301e-06 23.443164 24.160790
V-13_strong_increasing         NADA2 (R) 20.230187 2.034849e-06       NaN       NaN
  V-13_weak_decreasing MannKS (Standard) -2.241818 1.577977e-03 -2.505029 -1.973345
  V-13_weak_decreasing MannKS (LWP Mode) -2.096619 1.239009e-13 -2.375827 -1.818101
  V-13_weak_decreasing    LWP-TRENDS (R) -2.096619 4.877611e-14 -2.329167 -1.870403
  V-13_weak_decreasing      MannKS (ATS) -2.511369 1.577977e-03 -2.802027 -2.195951
  V-13_weak_decreasing         NADA2 (R) -1.523124 1.313942e-03       NaN       NaN
           V-13_stable MannKS (Standard)  0.208187 5.179169e-01 -0.231607  0.567539
           V-13_stable MannKS (LWP Mode)  0.009295 3.282304e-01 -0.011928  0.429140
           V-13_stable    LWP-TRENDS (R)  0.009295 3.202983e-01  0.000000  0.355311
           V-13_stable      MannKS (ATS)  0.132807 5.179169e-01 -0.147697  0.430087
           V-13_stable         NADA2 (R)  0.071246 5.109250e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-13_strong_increasing 0.000000e+00   0.000000e+00
  V-13_weak_decreasing 4.440892e-16  -2.220446e-13
           V-13_stable 1.734723e-18   1.866350e-14
