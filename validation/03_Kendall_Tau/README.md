# Validation Report

## Plots
### v03_combined.png
![v03_combined.png](v03_combined.png)

### v03_tied.png
![v03_tied.png](v03_tied.png)

## Results
                   Test ID                Method         Slope       P-Value      Lower CI      Upper CI
      V-03_step_increasing MannKenSen (Standard)  5.003425e+00  9.582494e-08  4.013736e+00  5.968137e+00
      V-03_step_increasing MannKenSen (LWP Mode)  5.003425e+00  9.582494e-08  4.013736e+00  5.968137e+00
      V-03_step_increasing        LWP-TRENDS (R)  5.003425e+00  1.311909e-08  4.286972e+00  5.467814e+00
      V-03_step_increasing      MannKenSen (ATS)  1.585490e-07  9.582494e-08  1.271876e-07  1.891189e-07
      V-03_step_increasing             NADA2 (R)  5.006854e+00  1.311909e-08           NaN           NaN
      V-03_step_decreasing MannKenSen (Standard) -5.003425e+00  9.582494e-08 -5.968137e+00 -4.013736e+00
      V-03_step_decreasing MannKenSen (LWP Mode) -5.003425e+00  9.582494e-08 -5.968137e+00 -4.013736e+00
      V-03_step_decreasing        LWP-TRENDS (R) -5.003425e+00  1.311909e-08 -5.642604e+00 -4.286972e+00
      V-03_step_decreasing      MannKenSen (ATS) -1.585490e-07  9.582494e-08 -1.891189e-07 -1.271876e-07
      V-03_step_decreasing             NADA2 (R) -5.006854e+00  1.311909e-08           NaN           NaN
                 V-03_flat MannKenSen (Standard)  0.000000e+00  1.000000e+00  0.000000e+00  0.000000e+00
                 V-03_flat MannKenSen (LWP Mode)  0.000000e+00  1.000000e+00  0.000000e+00  0.000000e+00
                 V-03_flat        LWP-TRENDS (R) -2.147484e+09 -2.147484e+09 -2.147484e+09 -2.147484e+09
                 V-03_flat      MannKenSen (ATS)  0.000000e+00  1.000000e+00  0.000000e+00  0.000000e+00
                 V-03_flat             NADA2 (R)  0.000000e+00           NaN           NaN           NaN
V-03_step_increasing_tau_a MannKenSen (Standard)  5.003425e+00  9.582494e-08  4.013736e+00  5.968137e+00
V-03_step_increasing_tau_a MannKenSen (LWP Mode)  5.003425e+00  9.582494e-08  4.013736e+00  5.968137e+00
V-03_step_increasing_tau_a        LWP-TRENDS (R)  5.003425e+00  1.311909e-08  4.286972e+00  5.467814e+00
V-03_step_increasing_tau_a      MannKenSen (ATS)  1.585490e-07  9.582494e-08  1.271876e-07  1.891189e-07
V-03_step_increasing_tau_a             NADA2 (R)  5.006854e+00  1.311909e-08           NaN           NaN

## LWP Accuracy (Python vs R)
                   Test ID  Slope Error  Slope % Error
      V-03_step_increasing          0.0            0.0
      V-03_step_decreasing          0.0           -0.0
                 V-03_flat 2147483648.0         -100.0
V-03_step_increasing_tau_a          0.0            0.0
