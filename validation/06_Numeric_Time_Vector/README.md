# Validation Report

## Plots
### v06_combined.png
![v06_combined.png](v06_combined.png)

### v06_strong.png
![v06_strong.png](v06_strong.png)

## Results
               Test ID                Method     Slope      P-Value  Lower CI  Upper CI
V-06_strong_increasing MannKenSen (Standard)  2.062331 4.294908e-09  1.898255  2.312101
V-06_strong_increasing MannKenSen (LWP Mode)  2.062331 4.294908e-09  1.897935  2.313583
V-06_strong_increasing        LWP-TRENDS (R)  1.997038 9.600847e-09  1.932658  2.062034
V-06_strong_increasing      MannKenSen (ATS)  2.062331 4.294908e-09  1.898255  2.312101
V-06_strong_increasing             NADA2 (R)  2.014219 4.294908e-09       NaN       NaN
  V-06_weak_decreasing MannKenSen (Standard) -0.195396 5.001957e-05 -0.270262 -0.131986
  V-06_weak_decreasing MannKenSen (LWP Mode) -0.195396 5.001957e-05 -0.270388 -0.130297
  V-06_weak_decreasing        LWP-TRENDS (R) -0.197641 5.001957e-05 -0.262600 -0.142035
  V-06_weak_decreasing      MannKenSen (ATS) -0.195396 5.001957e-05 -0.270262 -0.131986
  V-06_weak_decreasing             NADA2 (R) -0.197666 5.001957e-05       NaN       NaN
           V-06_stable MannKenSen (Standard) -0.043919 1.629844e-01 -0.101040  0.014660
           V-06_stable MannKenSen (LWP Mode) -0.043919 1.629844e-01 -0.101438  0.014756
           V-06_stable        LWP-TRENDS (R) -0.046151 1.629844e-01 -0.101955  0.010274
           V-06_stable      MannKenSen (ATS) -0.043919 1.629844e-01 -0.101040  0.014660
           V-06_stable             NADA2 (R) -0.046136 1.629844e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-06_strong_increasing     0.065293       3.264652
  V-06_weak_decreasing     0.002245      -1.122497
           V-06_stable     0.002233      -4.837556
