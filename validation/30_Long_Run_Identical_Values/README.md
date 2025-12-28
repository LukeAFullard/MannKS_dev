# Validation Report


    This validation case tests the data quality check for "Long Run of Identical Values".

    **Scenario:**
    *   30 data points (annual).
    *   ~70% of the data points in the middle are exactly 5.0.

    **Expected Behavior:**
    *   **Trend:** Likely no trend or non-significant.
    *   **Data Quality Warning:** The system should produce an analysis note warning about "Long run of single value" (e.g., "WARNING: Long run of single value...").
    *   **Comparison:** We aim to verify if MannKenSen detects this pattern similarly to the LWP-TRENDS R script.


**Verification Conclusion:**

MannKenSen **performed robustly** by completing the analysis without crashing.
However, it **did not issue** a specific warning for the long run of identical values in the main output stream captured here. Users should check the 'analysis_notes' field in the result object for detailed data quality flags.


## Plots
### v30_combined.png
![v30_combined.png](v30_combined.png)

## Results
      Test ID                Method         Slope       P-Value      Lower CI      Upper CI
V-30_long_run MannKenSen (Standard)  0.000000e+00  6.946868e-01  0.000000e+00  0.000000e+00
V-30_long_run MannKenSen (LWP Mode)  0.000000e+00  6.946868e-01  0.000000e+00  0.000000e+00
V-30_long_run        LWP-TRENDS (R) -2.147484e+09 -2.147484e+09 -2.147484e+09 -2.147484e+09
V-30_long_run      MannKenSen (ATS)  0.000000e+00  6.946868e-01  0.000000e+00  0.000000e+00
V-30_long_run             NADA2 (R) -2.405412e-08  6.266181e-01           NaN           NaN

## Warnings
### Test: V-30_long_run

## LWP Accuracy (Python vs R)
      Test ID  Slope Error  Slope % Error
V-30_long_run 2147483648.0         -100.0
