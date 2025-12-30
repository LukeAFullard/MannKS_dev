# Validation Report


**V-15: Quarterly Seasonal Data**

This test verifies the seasonal trend analysis functionality on a quarterly dataset.
It compares the standard `MannKS` seasonal test against the LWP-TRENDS R script and NADA2.


## Plots
### V15_Quarterly_Analysis.png
![V15_Quarterly_Analysis.png](V15_Quarterly_Analysis.png)

## Results
               Test ID            Method     Slope      P-Value  Lower CI  Upper CI
V-15_strong_increasing MannKS (Standard)  1.910039 4.085621e-14  1.789350  1.994029
V-15_strong_increasing MannKS (LWP Mode)  1.910039 4.085621e-14  1.790081  1.993836
V-15_strong_increasing    LWP-TRENDS (R)  1.910039 4.095980e-14  1.817034  1.985167
V-15_strong_increasing      MannKS (ATS)  1.913937 4.085621e-14  1.838856  1.985539
V-15_strong_increasing         NADA2 (R)  1.875000 2.000000e-03       NaN       NaN
  V-15_weak_decreasing MannKS (Standard) -0.475203 9.993144e-05 -0.644613 -0.226040
  V-15_weak_decreasing MannKS (LWP Mode) -0.475203 9.993144e-05 -0.644464 -0.226053
  V-15_weak_decreasing    LWP-TRENDS (R) -0.475203 9.993144e-05 -0.614886 -0.244627
  V-15_weak_decreasing      MannKS (ATS) -0.475202 9.993144e-05 -0.608166 -0.353833
  V-15_weak_decreasing         NADA2 (R) -0.560500 2.000000e-03       NaN       NaN
           V-15_stable MannKS (Standard)  0.037460 5.609859e-01 -0.066139  0.110834
           V-15_stable MannKS (LWP Mode)  0.037460 5.609859e-01 -0.065751  0.110107
           V-15_stable    LWP-TRENDS (R)  0.037460 5.609859e-01 -0.057653  0.093914
           V-15_stable      MannKS (ATS)  0.038390 5.609859e-01 -0.014045  0.107779
           V-15_stable         NADA2 (R) -0.009769 5.560000e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-15_strong_increasing 2.220446e-16   1.110223e-14
  V-15_weak_decreasing 0.000000e+00  -0.000000e+00
           V-15_stable 0.000000e+00   0.000000e+00
