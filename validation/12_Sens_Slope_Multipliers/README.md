# Validation Report


    # V-12: Sen's Slope Censored Multipliers

    ## Objective
    Isolate and verify the effect of the `lt_mult` and `gt_mult` parameters.
    The test uses data with **multiple censoring levels** (<1, <3, <5) to ensure
    robust validation of multiplier application across different limits.


## Plots
### plot_trend.png
![plot_trend.png](plot_trend.png)

### v12_combined.png
![v12_combined.png](v12_combined.png)

## Results
               Test ID            Method     Slope      P-Value  Lower CI  Upper CI
V-12_strong_increasing MannKS (Standard)  4.979739 5.633458e-08  4.544820  5.503678
V-12_strong_increasing MannKS (LWP Mode)  4.730108 5.633458e-08  4.279968  5.192207
V-12_strong_increasing    LWP-TRENDS (R)  4.730108 5.543813e-08  4.361927  5.116935
V-12_strong_increasing      MannKS (ATS)  4.814254 5.633458e-08  4.410159  5.234630
V-12_strong_increasing         NADA2 (R)  4.808163 5.543812e-08       NaN       NaN
  V-12_weak_decreasing MannKS (Standard) -3.503992 2.828936e-05 -4.058778 -2.952320
  V-12_weak_decreasing MannKS (LWP Mode) -2.898285 2.828936e-05 -3.425884  0.000000
  V-12_weak_decreasing    LWP-TRENDS (R) -2.898285 2.614663e-05 -3.319318 -1.482639
  V-12_weak_decreasing      MannKS (ATS) -3.155856 2.828936e-05 -3.562066 -2.752503
  V-12_weak_decreasing         NADA2 (R) -3.163687 2.614663e-05       NaN       NaN
           V-12_stable MannKS (Standard) -0.904107 5.454676e-01 -6.162732  4.676632
           V-12_stable MannKS (LWP Mode)  0.000000 5.454676e-01  0.000000  0.000000
           V-12_stable    LWP-TRENDS (R)  0.000000 5.344394e-01  0.000000  0.000000
           V-12_stable      MannKS (ATS) -0.669911 5.454676e-01 -2.119948  0.996864
           V-12_stable         NADA2 (R) -0.670698 5.344394e-01       NaN       NaN

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-12_strong_increasing 0.000000e+00   0.000000e+00
  V-12_weak_decreasing 4.440892e-16   1.532248e-14
           V-12_stable          NaN            NaN
