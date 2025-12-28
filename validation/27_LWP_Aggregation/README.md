# Validation Report


**V-27: LWP Aggregation (agg_method='lwp')**

This test verifies the LWP-style temporal aggregation behavior.
The dataset contains multiple observations per month. LWP Mode should aggregate these to a single value per month,
matching the behavior of the LWP-TRENDS R script.

**Scenarios:**
1.  **Strong Increasing:** Clear positive trend, multiple points per month.
2.  **Weak Decreasing:** Subtle negative trend, multiple points per month.
3.  **Stable:** No underlying trend, multiple points per month.


## Plots
### V27_LWP_Aggregation.png
![V27_LWP_Aggregation.png](V27_LWP_Aggregation.png)

## Results
               Test ID                Method     Slope      P-Value  Lower CI  Upper CI
V-27_strong_increasing MannKenSen (Standard)  2.037419 0.000000e+00  1.987814  2.078877
V-27_strong_increasing MannKenSen (LWP Mode)  2.043763 0.000000e+00  1.896587  2.109822
V-27_strong_increasing        LWP-TRENDS (R)  2.043763 3.943364e-17  1.932420  2.102689
V-27_strong_increasing      MannKenSen (ATS)  2.037404 0.000000e+00  2.016428  2.057874
V-27_strong_increasing             NADA2 (R)  2.038000 2.000000e-03       NaN       NaN
  V-27_weak_decreasing MannKenSen (Standard) -0.517081 1.776357e-15 -0.631757 -0.414257
  V-27_weak_decreasing MannKenSen (LWP Mode) -0.416533 4.302779e-06 -0.700141 -0.278365
  V-27_weak_decreasing        LWP-TRENDS (R) -0.416533 4.302779e-06 -0.682307 -0.294860
  V-27_weak_decreasing      MannKenSen (ATS) -0.517378 1.776357e-15 -0.563773 -0.463182
  V-27_weak_decreasing             NADA2 (R) -0.509100 2.000000e-03       NaN       NaN
           V-27_stable MannKenSen (Standard) -0.114998 1.576609e-02 -0.221758 -0.021062
           V-27_stable MannKenSen (LWP Mode) -0.185320 5.820666e-03 -0.495384 -0.050464
           V-27_stable        LWP-TRENDS (R) -0.185320 5.820666e-03 -0.462333 -0.088700
           V-27_stable      MannKenSen (ATS) -0.115316 1.576609e-02 -0.154215 -0.081039
           V-27_stable             NADA2 (R) -0.119800 1.400000e-02       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID   Slope Error  Slope % Error
V-27_strong_increasing -4.440892e-16  -2.220446e-14
  V-27_weak_decreasing  0.000000e+00  -0.000000e+00
           V-27_stable -2.775558e-17   1.497709e-14
