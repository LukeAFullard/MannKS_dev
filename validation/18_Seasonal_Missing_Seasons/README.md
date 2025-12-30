# Validation Report


**V-18: Seasonal Data with Missing Seasons**

This test verifies the seasonal trend analysis when entire seasons are missing from the dataset.
Specifically, all data for **July (Month 7)** and **August (Month 8)** will be removed.
This forces the test to skip these seasons and only analyze the remaining 10 months.

**Note:** The LWP-TRENDS R script has a known fragility with missing seasons and may fail to run.
The `MannKS` package is expected to handle this gracefully by skipping the missing seasons and analyzing the rest.

**R Workaround:** To verify if the LWP R script *can* run if the data is massaged, this validation
script also runs a "Patched" version where missing seasons are filled with `NA` values to ensure
a complete Year x Month grid. This confirms that the R failure is structural, not statistical.


## Plots
### V18_Missing_Seasons_Analysis.png
![V18_Missing_Seasons_Analysis.png](V18_Missing_Seasons_Analysis.png)

## Results
               Test ID                   Method     Slope      P-Value  Lower CI  Upper CI
V-18_strong_increasing        MannKS (Standard)  2.009240 0.000000e+00  1.945708  2.103445
V-18_strong_increasing        MannKS (LWP Mode)  2.009240 0.000000e+00  1.945971  2.103323
V-18_strong_increasing           LWP-TRENDS (R)       NaN          NaN       NaN       NaN
V-18_strong_increasing LWP-TRENDS (R) [Patched]  2.020100 1.485100e-41  1.977729  2.086202
V-18_strong_increasing             MannKS (ATS)  2.009473 0.000000e+00  1.984257  2.041560
V-18_strong_increasing                NADA2 (R)  1.977000 2.000000e-03       NaN       NaN
  V-18_weak_decreasing        MannKS (Standard) -0.504437 4.082930e-10 -0.658350 -0.354837
  V-18_weak_decreasing        MannKS (LWP Mode) -0.504437 4.082930e-10 -0.655193 -0.356238
  V-18_weak_decreasing           LWP-TRENDS (R)       NaN          NaN       NaN       NaN
  V-18_weak_decreasing LWP-TRENDS (R) [Patched] -0.533662 5.752858e-14 -0.623849 -0.431508
  V-18_weak_decreasing             MannKS (ATS) -0.504562 4.082930e-10 -0.556524 -0.471659
  V-18_weak_decreasing                NADA2 (R) -0.565200 2.000000e-03       NaN       NaN
           V-18_stable        MannKS (Standard) -0.046364 3.506233e-01 -0.114749  0.044936
           V-18_stable        MannKS (LWP Mode) -0.046364 3.506233e-01 -0.113451  0.044727
           V-18_stable           LWP-TRENDS (R)       NaN          NaN       NaN       NaN
           V-18_stable LWP-TRENDS (R) [Patched] -0.037174 3.941828e-01 -0.085014  0.027532
           V-18_stable             MannKS (ATS) -0.046626 3.506233e-01 -0.070598 -0.022655
           V-18_stable                NADA2 (R) -0.106200 3.740000e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-18_strong_increasing          NaN            NaN
  V-18_weak_decreasing          NaN            NaN
           V-18_stable          NaN            NaN
