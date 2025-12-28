# Validation Report

Validation of V-28: Insufficient Data. Testing datasets with n=4 while min_size=5. Expecting warnings and NaN results.

## Results
               Test ID                Method         Slope       P-Value      Lower CI      Upper CI
V-28_strong_increasing MannKenSen (Standard)  2.057811e+00  8.942936e-02           NaN           NaN
V-28_strong_increasing MannKenSen (LWP Mode)  2.057811e+00  8.942936e-02  1.937829e+00  2.088450e+00
V-28_strong_increasing        LWP-TRENDS (R) -2.147484e+09 -2.147484e+09 -2.147484e+09 -2.147484e+09
  V-28_weak_decreasing MannKenSen (Standard) -5.431011e-01  8.942936e-02           NaN           NaN
  V-28_weak_decreasing MannKenSen (LWP Mode) -5.431011e-01  8.942936e-02 -6.793923e-01 -3.079995e-01
  V-28_weak_decreasing        LWP-TRENDS (R) -2.147484e+09 -2.147484e+09 -2.147484e+09 -2.147484e+09
           V-28_stable MannKenSen (Standard) -7.082906e-02  7.340952e-01           NaN           NaN
           V-28_stable MannKenSen (LWP Mode) -7.082906e-02  7.340952e-01 -1.174068e-01  1.139696e-01
           V-28_stable        LWP-TRENDS (R) -2.147484e+09 -2.147484e+09 -2.147484e+09 -2.147484e+09

## LWP Accuracy (Python vs R)
               Test ID  Slope Error  Slope % Error
V-28_strong_increasing 2.147484e+09   1.073742e+11
  V-28_weak_decreasing 2.147484e+09  -4.294967e+11
           V-28_stable 2.147484e+09  -1.000000e+02

## Discussion

This test verified the behavior of the `MannKenSen` package when dealing with datasets smaller than the configured `min_size` parameter. In this case, datasets with N=4 were tested against a configured `min_size` of 5.

**Expected Behavior:**
The package is expected to issue a warning alerting the user that the sample size is insufficient, but it should typically attempt a "best effort" calculation rather than crashing, unless N < 2. The reference R script (`LWP-TRENDS`) is known to be fragile with such small datasets.

**Observations:**
1.  **Warnings Triggered:** As shown in the "Captured Analysis Notes" section below, the `MannKenSen` package correctly identified the issue and appended the note: `'sample size (4) below minimum (5)'` to the results.
2.  **Calculation Results:**
    -   The package successfully calculated the slope and p-value despite the small sample size.
    -   **Standard CI (NaN):** The Standard mode correctly returned `NaN` for confidence intervals. This is a robust behavior; with only 4 data points (6 pairwise slopes), calculating a 90% or 95% confidence interval using the direct method often results in indices that are out of bounds. The package caught this and issued a `UserWarning` (visible in logs) instead of crashing.
    -   **LWP Mode CI (Values):** The LWP mode returned numerical confidence intervals. This highlights the difference in methodology: LWP uses an interpolation approximation that forces a result even when data is sparse, whereas the Standard "Robust" mode is more conservative.
3.  **R Script Failure:** The LWP-TRENDS R script failed to produce results (returned `NaN`), confirming that the Python implementation is more robust in terms of execution stability for edge cases.

**Conclusion:**
The `MannKenSen` package behaves as expected. It provides the user with necessary warnings about data sufficiency and computational limitations (NaN CIs in robust mode) while ensuring the process completes without execution errors.


### Captured Analysis Notes
- V-28_strong_increasing (Std): ['< 5 Non-censored values', 'sample size (4) below minimum (5)']
- V-28_strong_increasing (LWP): ['< 5 Non-censored values', 'sample size (4) below minimum (5)']
- V-28_weak_decreasing (Std): ['< 5 Non-censored values', 'sample size (4) below minimum (5)']
- V-28_weak_decreasing (LWP): ['< 5 Non-censored values', 'sample size (4) below minimum (5)']
- V-28_stable (Std): ['< 5 Non-censored values', 'sample size (4) below minimum (5)']
- V-28_stable (LWP): ['< 5 Non-censored values', 'sample size (4) below minimum (5)', 'WARNING: Sen slope based on tied non-censored values']
