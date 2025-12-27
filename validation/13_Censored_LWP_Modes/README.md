# Validation Report


# Validation Case V-13: Censored LWP Compatibility Modes

This validation case focuses on verifying the "LWP Compatibility Mode" of the `mannkensen` package against the original LWP-TRENDS R script, specifically for **right-censored** data.

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
               Test ID                Method         Slope      P-Value      Lower CI      Upper CI
V-13_strong_increasing MannKenSen (Standard)  2.290743e+01 2.988301e-06  2.166883e+01  2.366761e+01
V-13_strong_increasing MannKenSen (LWP Mode)  2.233000e+01 0.000000e+00  2.081536e+01  2.335437e+01
V-13_strong_increasing        LWP-TRENDS (R)  2.233000e+01 8.450761e-20  2.115055e+01  2.318617e+01
V-13_strong_increasing      MannKenSen (ATS)  7.547076e-07 2.988301e-06  7.429859e-07  7.666314e-07
V-13_strong_increasing             NADA2 (R)  2.023019e+01 2.034849e-06           NaN           NaN
  V-13_weak_decreasing MannKenSen (Standard) -2.241818e+00 1.577977e-03 -2.505029e+00 -1.973345e+00
  V-13_weak_decreasing MannKenSen (LWP Mode) -2.096619e+00 1.239009e-13 -2.375827e+00 -1.818101e+00
  V-13_weak_decreasing        LWP-TRENDS (R) -2.096619e+00 4.877611e-14 -2.329167e+00 -1.870403e+00
  V-13_weak_decreasing      MannKenSen (ATS) -7.958050e-08 1.577977e-03 -8.802517e-08 -7.033250e-08
  V-13_weak_decreasing             NADA2 (R) -1.523124e+00 1.313942e-03           NaN           NaN
           V-13_stable MannKenSen (Standard)  2.081871e-01 5.179169e-01 -2.316072e-01  5.675388e-01
           V-13_stable MannKenSen (LWP Mode)  9.294736e-03 3.282304e-01 -1.192797e-02  4.291403e-01
           V-13_stable        LWP-TRENDS (R)  9.294736e-03 3.202983e-01  0.000000e+00  3.553108e-01
           V-13_stable      MannKenSen (ATS)  4.208411e-09 5.179169e-01 -3.398805e-09  1.255751e-08
           V-13_stable             NADA2 (R)  7.124561e-02 5.109250e-01           NaN           NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-13_strong_increasing 0.000000e+00   0.000000e+00
  V-13_weak_decreasing 4.440892e-16  -2.220446e-13
           V-13_stable 1.734723e-18   1.866350e-14
