# Validation Report

## Plots
### v01_combined.png
![v01_combined.png](v01_combined.png)

### v01_strong.png
![v01_strong.png](v01_strong.png)

## Results
               Test ID                Method         Slope      P-Value      Lower CI      Upper CI
V-01_strong_increasing MannKenSen (Standard)  1.907946e+00 1.302558e-09  1.833785e+00  1.967454e+00
V-01_strong_increasing MannKenSen (LWP Mode)  1.907946e+00 1.302558e-09  1.832234e+00  1.967468e+00
V-01_strong_increasing        LWP-TRENDS (R)  1.907946e+00 1.302558e-09  1.840376e+00  1.960270e+00
V-01_strong_increasing      MannKenSen (ATS)  6.045916e-08 1.302558e-09  5.810913e-08  6.234486e-08
V-01_strong_increasing             NADA2 (R)  1.907534e+00 1.302558e-09           NaN           NaN
  V-01_weak_decreasing MannKenSen (Standard) -2.399869e-01 8.645690e-05 -3.151898e-01 -1.494008e-01
  V-01_weak_decreasing MannKenSen (LWP Mode) -2.399869e-01 8.645690e-05 -3.168452e-01 -1.483773e-01
  V-01_weak_decreasing        LWP-TRENDS (R) -2.399869e-01 8.645690e-05 -3.070945e-01 -1.681561e-01
  V-01_weak_decreasing      MannKenSen (ATS) -7.604727e-09 8.645690e-05 -9.987761e-09 -4.734227e-09
  V-01_weak_decreasing             NADA2 (R) -2.400987e-01 8.645690e-05           NaN           NaN
           V-01_stable MannKenSen (Standard)  1.893143e-02 5.376032e-01 -4.935604e-02  9.555398e-02
           V-01_stable MannKenSen (LWP Mode)  1.893143e-02 5.376032e-01 -4.983438e-02  9.561310e-02
           V-01_stable        LWP-TRENDS (R)  1.893143e-02 5.376032e-01 -3.880886e-02  8.193496e-02
           V-01_stable      MannKenSen (ATS)  5.999009e-10 5.376032e-01 -1.563998e-09  3.027923e-09
           V-01_stable             NADA2 (R)  1.890128e-02 5.376032e-01           NaN           NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-01_strong_increasing 0.000000e+00   0.000000e+00
  V-01_weak_decreasing 2.775558e-17  -1.387779e-14
           V-01_stable 0.000000e+00   0.000000e+00
