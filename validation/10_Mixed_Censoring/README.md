# Validation Report

## Plots
### V-10_strong_increasing_plot.png
![V-10_strong_increasing_plot.png](V-10_strong_increasing_plot.png)

### v10_combined.png
![v10_combined.png](v10_combined.png)

## Results
               Test ID                Method         Slope      P-Value      Lower CI      Upper CI
V-10_Strong_Increasing MannKenSen (Standard)  2.715002e+00 2.820633e-12  2.458262e+00  2.951087e+00
V-10_Strong_Increasing MannKenSen (LWP Mode)  2.329119e+00 1.885788e-09  1.952902e+00  2.618307e+00
V-10_Strong_Increasing        LWP-TRENDS (R)  2.361821e+00 4.043957e-09  2.054941e+00  2.611265e+00
V-10_Strong_Increasing      MannKenSen (ATS)  7.973650e-08 2.820633e-12  7.392204e-08  8.520985e-08
V-10_Strong_Increasing             NADA2 (R)  2.519028e+00 2.820633e-12           NaN           NaN
  V-10_Weak_Decreasing MannKenSen (Standard) -3.655599e-01 3.323502e-03 -8.110110e-01 -6.141331e-02
  V-10_Weak_Decreasing MannKenSen (LWP Mode)  0.000000e+00 5.695740e-02 -1.602645e-01  0.000000e+00
  V-10_Weak_Decreasing        LWP-TRENDS (R)  0.000000e+00 5.961479e-02 -9.909215e-02  0.000000e+00
  V-10_Weak_Decreasing      MannKenSen (ATS) -1.713688e-08 3.323502e-03 -2.707421e-08 -7.558835e-09
  V-10_Weak_Decreasing             NADA2 (R) -6.719097e-01 3.323502e-03           NaN           NaN
           V-10_Stable MannKenSen (Standard)  1.553205e-01 4.626341e-01 -1.386732e-01  3.722602e-01
           V-10_Stable MannKenSen (LWP Mode)  0.000000e+00 2.816365e-01  0.000000e+00  0.000000e+00
           V-10_Stable        LWP-TRENDS (R)  0.000000e+00 1.511017e-01  0.000000e+00  0.000000e+00
           V-10_Stable      MannKenSen (ATS)  5.598340e-09 4.626341e-01  6.187720e-11  1.157097e-08
           V-10_Stable             NADA2 (R)  1.193552e-01 4.626341e-01           NaN           NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-10_Strong_Increasing    -0.032702     -16.351207
  V-10_Weak_Decreasing     0.000000      -0.000000
           V-10_Stable     0.000000       0.000000
