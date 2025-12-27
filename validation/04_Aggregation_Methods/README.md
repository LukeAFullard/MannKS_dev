# Validation Case V-04: Aggregation Methods

## Case Description
This validation case verifies the `agg_method` options for handling multiple observations per time period, specifically comparing the standard MannKenSen behavior against the LWP-TRENDS R script which enforces aggregation (e.g., one value per month). To ensure deterministic results, observations are distributed throughout the month, avoiding identical timestamps and ambiguous tie-breaking.

Three scenarios were tested:
1.  **Strong Increasing Trend:** A clear, statistically significant positive trend.
2.  **Weak Decreasing Trend:** A subtle, statistically significant (or borderline) negative trend.
3.  **Stable (No Trend):** Data with no underlying trend.

## Combined Results
![Combined Trend Analysis](v04_combined.png)

## Results Table
               Test ID                Method         Slope      P-Value      Lower CI      Upper CI
V-04_Strong_Increasing MannKenSen (Standard)  5.471819e+00 0.000000e+00  5.069618e+00  5.887400e+00
V-04_Strong_Increasing MannKenSen (LWP Mode)  5.347630e+00 8.096543e-10  4.271008e+00  6.261226e+00
V-04_Strong_Increasing        LWP-TRENDS (R)  5.347630e+00 8.096542e-10  4.512288e+00  6.183789e+00
V-04_Strong_Increasing      MannKenSen (ATS)  1.733915e-07 0.000000e+00  1.606465e-07  1.865605e-07
V-04_Strong_Increasing             NADA2 (R)  5.475132e+00 0.000000e+00           NaN           NaN
  V-04_Weak_Decreasing MannKenSen (Standard) -7.492270e-01 9.568603e-04 -1.196668e+00 -3.015777e-01
  V-04_Weak_Decreasing MannKenSen (LWP Mode) -8.059070e-01 1.237650e-01 -1.713867e+00  2.253121e-01
  V-04_Weak_Decreasing        LWP-TRENDS (R) -8.059070e-01 1.237650e-01 -1.627620e+00  7.439765e-02
  V-04_Weak_Decreasing      MannKenSen (ATS) -2.374157e-08 9.568603e-04 -3.792011e-08 -9.556421e-09
  V-04_Weak_Decreasing             NADA2 (R) -7.495176e-01 9.568603e-04           NaN           NaN
           V-04_Stable MannKenSen (Standard) -2.587379e-01 2.171840e-01 -6.722748e-01  1.502797e-01
           V-04_Stable MannKenSen (LWP Mode) -5.285181e-01 1.449962e-01 -1.191366e+00  1.766613e-01
           V-04_Stable        LWP-TRENDS (R) -5.285181e-01 1.449962e-01 -1.141315e+00  4.620968e-02
           V-04_Stable      MannKenSen (ATS) -8.198908e-09 2.171840e-01 -2.130310e-08  4.762075e-09
           V-04_Stable             NADA2 (R) -2.587903e-01 2.171840e-01           NaN           NaN

## LWP Accuracy (Python vs R)
               Test ID   Slope Error  Slope % Error
V-04_Strong_Increasing  0.000000e+00   0.000000e+00
  V-04_Weak_Decreasing  1.110223e-16  -9.251859e-15
           V-04_Stable -1.110223e-16   2.100634e-14
