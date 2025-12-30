# Validation Report


**V-16: Monthly Seasonal with Left-Censoring**

This test verifies the seasonal trend analysis functionality on a monthly dataset containing left-censored values (e.g., '<5').
It compares the standard `MannKS` seasonal test against the LWP-TRENDS R script and NADA2.


## Plots
### V16_Censored_Seasonal_Analysis.png
![V16_Censored_Seasonal_Analysis.png](V16_Censored_Seasonal_Analysis.png)

## Results
               Test ID            Method     Slope      P-Value  Lower CI  Upper CI
V-16_strong_increasing MannKS (Standard)  2.064607 0.000000e+00  1.986179  2.161971
V-16_strong_increasing MannKS (LWP Mode)  2.038905 0.000000e+00  1.966021  2.129612
V-16_strong_increasing    LWP-TRENDS (R)  2.038905 1.032187e-39  1.977236  2.118986
V-16_strong_increasing      MannKS (ATS)  2.011407 0.000000e+00  1.987428  2.039605
V-16_strong_increasing         NADA2 (R)  1.909000 2.000000e-03       NaN       NaN
  V-16_weak_decreasing MannKS (Standard) -0.560275 3.308069e-05 -0.780844 -0.332092
  V-16_weak_decreasing MannKS (LWP Mode)  0.000000 3.308069e-05  0.000000  0.000000
  V-16_weak_decreasing    LWP-TRENDS (R)  0.000000 2.649001e-05  0.000000  0.000000
  V-16_weak_decreasing      MannKS (ATS) -0.533913 3.308069e-05 -0.562469 -0.488219
  V-16_weak_decreasing         NADA2 (R) -0.673900 2.000000e-03       NaN       NaN
           V-16_stable MannKS (Standard) -0.011602 7.759849e-01 -0.163160  0.118042
           V-16_stable MannKS (LWP Mode)  0.000000 7.759849e-01  0.000000  0.000000
           V-16_stable    LWP-TRENDS (R)  0.000000 7.697619e-01  0.000000  0.000000
           V-16_stable      MannKS (ATS) -0.011602 7.759849e-01 -0.035416  0.011580
           V-16_stable         NADA2 (R) -0.114400 6.700000e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-16_strong_increasing          0.0            0.0
  V-16_weak_decreasing          0.0           -0.0
           V-16_stable          0.0            0.0
