# Validation Report


**V-17: Monthly Seasonal with Right-Censoring**

This test verifies the seasonal trend analysis functionality on a monthly dataset containing right-censored values (e.g., '>100').
It compares the standard `MannKS` seasonal test against the LWP-TRENDS R script and NADA2.


## Plots
### V17_Right_Censored_Seasonal_Analysis.png
![V17_Right_Censored_Seasonal_Analysis.png](V17_Right_Censored_Seasonal_Analysis.png)

## Results
               Test ID            Method     Slope      P-Value  Lower CI  Upper CI
V-17_strong_increasing MannKS (Standard)  2.110343 4.729550e-14  2.021498  2.217530
V-17_strong_increasing MannKS (LWP Mode)  1.853979 0.000000e+00  1.669158  1.974966
V-17_strong_increasing    LWP-TRENDS (R)  1.853979 1.013892e-19  1.711629  1.957350
V-17_strong_increasing      MannKS (ATS)  2.053811 4.729550e-14  2.038237  2.067274
V-17_strong_increasing         NADA2 (R)  1.612000 2.000000e-03       NaN       NaN
  V-17_weak_decreasing MannKS (Standard) -0.496180 7.062206e-10 -0.631693 -0.373270
  V-17_weak_decreasing MannKS (LWP Mode) -0.489449 6.471024e-11 -0.625190 -0.365866
  V-17_weak_decreasing    LWP-TRENDS (R) -0.489449 6.471022e-11 -0.617886 -0.381726
  V-17_weak_decreasing      MannKS (ATS) -0.489428 7.062206e-10 -0.531849 -0.440601
  V-17_weak_decreasing         NADA2 (R) -0.509600 2.000000e-03       NaN       NaN
           V-17_stable MannKS (Standard) -0.000745 1.000000e+00 -0.067650  0.073621
           V-17_stable MannKS (LWP Mode)  0.000000 9.794010e-01 -0.062407  0.063569
           V-17_stable    LWP-TRENDS (R)  0.000000 9.793412e-01 -0.054445  0.055420
           V-17_stable      MannKS (ATS) -0.000656 1.000000e+00 -0.025921  0.020887
           V-17_stable         NADA2 (R) -0.067160 1.000000e+00       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-17_strong_increasing          0.0            0.0
  V-17_weak_decreasing          0.0           -0.0
           V-17_stable          0.0            0.0
