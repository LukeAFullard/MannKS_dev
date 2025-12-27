# Validation Report

## Plots
### stable.png
![stable.png](stable.png)

### strong_increasing.png
![strong_increasing.png](strong_increasing.png)

### v07_combined.png
![v07_combined.png](v07_combined.png)

### weak_decreasing.png
![weak_decreasing.png](weak_decreasing.png)

## Results
               Test ID                Method     Slope      P-Value  Lower CI  Upper CI
V-07_strong_increasing MannKenSen (Standard)  2.011795 0.000000e+00  1.983658  2.041160
V-07_strong_increasing MannKenSen (LWP Mode)  2.011795 0.000000e+00  1.983656  2.041165
V-07_strong_increasing        LWP-TRENDS (R)  2.011795 3.288877e-54  1.988568  2.036068
V-07_strong_increasing      MannKenSen (ATS)  2.011795 0.000000e+00  1.983658  2.041160
V-07_strong_increasing             NADA2 (R)  2.011828 0.000000e+00       NaN       NaN
  V-07_weak_decreasing MannKenSen (Standard) -0.471572 1.554312e-15 -0.568274 -0.388300
  V-07_weak_decreasing MannKenSen (LWP Mode) -0.471572 1.554312e-15 -0.568319 -0.388299
  V-07_weak_decreasing        LWP-TRENDS (R) -0.471572 1.494455e-15 -0.553832 -0.401151
  V-07_weak_decreasing      MannKenSen (ATS) -0.471572 1.554312e-15 -0.568274 -0.388300
  V-07_weak_decreasing             NADA2 (R) -0.471554 1.554312e-15       NaN       NaN
           V-07_stable MannKenSen (Standard) -0.004964 8.435639e-01 -0.065289  0.053756
           V-07_stable MannKenSen (LWP Mode) -0.004964 8.435639e-01 -0.065293  0.053762
           V-07_stable        LWP-TRENDS (R) -0.004964 8.435639e-01 -0.055981  0.044541
           V-07_stable      MannKenSen (ATS) -0.004964 8.435639e-01 -0.065289  0.053756
           V-07_stable             NADA2 (R) -0.004963 8.435639e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-07_strong_increasing 4.440892e-16   2.220446e-14
  V-07_weak_decreasing 5.551115e-17  -1.110223e-14
           V-07_stable 8.673617e-19  -1.747397e-14
