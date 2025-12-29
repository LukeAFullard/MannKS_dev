# Validation Report


**V-19: Alternative Seasonal Patterns (season_type='week_of_year')**

This test verifies the handling of 'week_of_year' seasonality.
The data is generated with a weekly frequency and a clear seasonal pattern across the 52 weeks of the year.
This tests the robustness of the datetime handling and the flexibility of the seasonal configuration.

**Scenarios:**
1.  **Strong Increasing:** Clear positive trend with weekly seasonality.
2.  **Weak Decreasing:** Subtle negative trend with weekly seasonality.
3.  **Stable:** No underlying trend, just weekly seasonality.


## Plots
### V19_Alternative_Seasonality.png
![V19_Alternative_Seasonality.png](V19_Alternative_Seasonality.png)

## Results
               Test ID                Method     Slope  P-Value  Lower CI  Upper CI
V-19_strong_increasing MannKS (Standard)  5.076052 0.000000  4.991450  5.198131
V-19_strong_increasing MannKS (LWP Mode)  5.076052 0.000000  4.991921  5.196357
V-19_strong_increasing        LWP-TRENDS (R)       NaN      NaN       NaN       NaN
V-19_strong_increasing      MannKS (ATS)  5.075987 0.000000  5.075987  5.075987
V-19_strong_increasing             NADA2 (R)  4.709000 0.002000       NaN       NaN
  V-19_weak_decreasing MannKS (Standard) -1.046334 0.000000 -1.142973 -0.961670
  V-19_weak_decreasing MannKS (LWP Mode) -1.046334 0.000000 -1.141933 -0.961854
  V-19_weak_decreasing        LWP-TRENDS (R)       NaN      NaN       NaN       NaN
  V-19_weak_decreasing      MannKS (ATS) -1.047034 0.000000 -1.047034 -1.047034
  V-19_weak_decreasing             NADA2 (R) -1.385000 0.002000       NaN       NaN
           V-19_stable MannKS (Standard)  0.012013 0.658787 -0.078212  0.099271
           V-19_stable MannKS (LWP Mode)  0.012013 0.658787 -0.077952  0.099094
           V-19_stable        LWP-TRENDS (R)       NaN      NaN       NaN       NaN
           V-19_stable      MannKS (ATS)  0.012648 0.658787  0.012648  0.012648
           V-19_stable             NADA2 (R) -0.336100 0.662000       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-19_strong_increasing          NaN            NaN
  V-19_weak_decreasing          NaN            NaN
           V-19_stable          NaN            NaN
