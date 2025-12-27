# Validation Report


    # V-08: Left-Censored Trend

    This validation case tests the package's ability to handle left-censored data (values reported as less than a detection limit, e.g., `<5.0`).

    Three scenarios were tested with updated parameters to ensure robust detectability:
    1. **Strong Increasing Trend**: Slope 5.0, Noise 1.0. Clear positive trend.
    2. **Weak Decreasing Trend**: Slope -0.8, Noise 0.5. Detectable negative trend (avoiding zero-slope artifacts from high noise).
    3. **Stable (No Trend)**: Slope 0.0, Noise 1.0. No underlying trend.


## Plots
### v08_combined.png
![v08_combined.png](v08_combined.png)

### v08_strong_left_censored.png
![v08_strong_left_censored.png](v08_strong_left_censored.png)

## Results
               Test ID                Method         Slope      P-Value      Lower CI      Upper CI
V-08_strong_increasing MannKenSen (Standard)  5.643887e+00 2.573497e-13  4.850932e+00  6.987687e+00
V-08_strong_increasing MannKenSen (LWP Mode)  5.489809e+00 2.573497e-13  4.735198e+00  6.814860e+00
V-08_strong_increasing        LWP-TRENDS (R)  5.489809e+00 2.115009e-13  4.860028e+00  6.606200e+00
V-08_strong_increasing      MannKenSen (ATS)  1.548638e-07 2.573497e-13  1.430536e-07  1.660990e-07
V-08_strong_increasing             NADA2 (R)  4.889521e+00 2.116085e-13           NaN           NaN
  V-08_weak_decreasing MannKenSen (Standard) -1.140265e+00 7.568782e-08 -2.127843e+00 -7.046380e-01
  V-08_weak_decreasing MannKenSen (LWP Mode) -1.074080e+00 7.568782e-08 -1.890429e+00 -6.651274e-01
  V-08_weak_decreasing        LWP-TRENDS (R) -1.074080e+00 6.798504e-08 -1.690951e+00 -7.094681e-01
  V-08_weak_decreasing      MannKenSen (ATS) -2.508113e-08 7.568782e-08 -3.117591e-08 -1.931139e-08
  V-08_weak_decreasing             NADA2 (R) -7.934790e-01 6.798504e-08           NaN           NaN
           V-08_stable MannKenSen (Standard) -3.740440e-01 2.749208e-01 -1.031641e+00  2.798449e-01
           V-08_stable MannKenSen (LWP Mode) -2.926753e-01 2.749208e-01 -9.215355e-01  1.531956e-01
           V-08_stable        LWP-TRENDS (R) -2.926753e-01 2.732017e-01 -8.122428e-01  9.518579e-02
           V-08_stable      MannKenSen (ATS) -1.081308e-08 2.749208e-01 -2.338827e-08  2.926638e-09
           V-08_stable             NADA2 (R) -3.414792e-01 2.732017e-01           NaN           NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-08_strong_increasing 0.000000e+00   0.000000e+00
  V-08_weak_decreasing 2.220446e-16  -2.775558e-14
           V-08_stable 0.000000e+00  -0.000000e+00
