# V-11: High Censor Rule

## Objective
Verify the implementation of the 'High Censor Rule' (`hicensor=True`). This rule, used in older LWP-TRENDS versions, sets all values below the highest detection limit to be censored at that highest limit. This prevents spurious trends caused solely by changing detection limits (e.g., detection limit improves from <5 to <1 over time).

## Plots
### v11_combined.png
![v11_combined.png](v11_combined.png)

## Results
               Test ID            Method     Slope      P-Value  Lower CI  Upper CI
V-11_strong_increasing MannKS (Standard)  0.865484 0.000000e+00  0.787276  0.948784
V-11_strong_increasing MannKS (LWP Mode)  0.791823 0.000000e+00  0.688459  0.881396
V-11_strong_increasing    LWP-TRENDS (R)  0.791823 3.497180e-24  0.713381  0.862459
V-11_strong_increasing      MannKS (ATS)  0.834950 0.000000e+00  0.764861  0.906293
V-11_strong_increasing         NADA2 (R)  0.835051 0.000000e+00       NaN       NaN
  V-11_weak_decreasing MannKS (Standard) -0.766328 2.220446e-16 -0.851204 -0.679787
  V-11_weak_decreasing MannKS (LWP Mode) -0.699787 6.661338e-16 -0.804780 -0.495237
  V-11_weak_decreasing    LWP-TRENDS (R) -0.699787 1.871089e-18 -0.782240 -0.570792
  V-11_weak_decreasing      MannKS (ATS) -0.720333 2.220446e-16 -0.802274 -0.639441
  V-11_weak_decreasing         NADA2 (R) -0.720507 2.220446e-16       NaN       NaN
           V-11_stable MannKS (Standard)  0.098476 1.479889e-01 -0.031943  0.234739
           V-11_stable MannKS (LWP Mode)  0.000000 1.674814e-01  0.000000  0.083402
           V-11_stable    LWP-TRENDS (R)  0.000000 1.558819e-01  0.000000  0.053588
           V-11_stable      MannKS (ATS)  0.090380 1.479889e-01 -0.022988  0.208181
           V-11_stable         NADA2 (R)  0.090405 1.476627e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-11_strong_increasing 1.110223e-16   1.402110e-14
  V-11_weak_decreasing 0.000000e+00  -0.000000e+00
           V-11_stable 0.000000e+00   0.000000e+00
