# Validation Report


# Validation Case V-13: Censored LWP Compatibility Modes

This validation case focuses on verifying the "LWP Compatibility Mode" of the `mannkensen` package against the original LWP-TRENDS R script, specifically for **right-censored** data.

The goal is to demonstrate that setting parameters `mk_test_method='lwp'` and `sens_slope_method='lwp'` allows Python to accurately replicate the R script's handling of censored values.

## Methodology
- **Data:** 4 years of monthly data (n=48).
- **Censoring:** Approximately 30% of data is **right-censored** (values above a threshold are marked as `>Threshold`).
- **Comparisons:**
    1. **MannKenSen (Standard):** Uses 'robust' MK test and standard Sen's slope.
    2. **MannKenSen (LWP Mode):** Uses `mk_test_method='lwp'` and `sens_slope_method='lwp'`.
    3. **LWP-TRENDS (R):** The reference R script.
    4. **MannKenSen (ATS):** Akritas-Theil-Sen method.
    5. **NADA2 (R):** The NADA2 reference R script.

**Note:** The plot below displays the **Standard** MannKenSen results on the raw data, as requested.


## Plots
### v13_strong.png
![v13_strong.png](v13_strong.png)

## Results
| Test ID                | Method                |       Slope |     P-Value |   Lower CI |   Upper CI |
|:-----------------------|:----------------------|------------:|------------:|-----------:|-----------:|
| V-13_strong_increasing | MannKenSen (Standard) | 22.896      | 2.9883e-06  |  21.6446   |  23.6848   |
| V-13_strong_increasing | MannKenSen (LWP Mode) | 22.33       | 0           |  20.8154   |  23.3544   |
| V-13_strong_increasing | LWP-TRENDS (R)        | 22.33       | 8.45076e-20 |  21.1505   |  23.1862   |
| V-13_strong_increasing | MannKenSen (ATS)      | 23.8352     | 2.9883e-06  |  23.474    |  24.1543   |
| V-13_strong_increasing | NADA2 (R)             | 20.2302     | 2.03485e-06 | nan        | nan        |
| V-13_weak_decreasing   | MannKenSen (Standard) | -2.2405     | 0.00157798  |  -2.50645  |  -1.97372  |
| V-13_weak_decreasing   | MannKenSen (LWP Mode) | -2.09662    | 1.23901e-13 |  -2.37583  |  -1.8181   |
| V-13_weak_decreasing   | LWP-TRENDS (R)        | -2.09662    | 4.87761e-14 |  -2.32917  |  -1.8704   |
| V-13_weak_decreasing   | MannKenSen (ATS)      | -2.50989    | 0.00157798  |  -2.83793  |  -2.20837  |
| V-13_weak_decreasing   | NADA2 (R)             | -1.52312    | 0.00131394  | nan        | nan        |
| V-13_stable            | MannKenSen (Standard) |  0.208236   | 0.517917    |  -0.231449 |   0.567944 |
| V-13_stable            | MannKenSen (LWP Mode) |  0.00929474 | 0.32823     |  -0.011928 |   0.42914  |
| V-13_stable            | LWP-TRENDS (R)        |  0.00929474 | 0.320298    |   0        |   0.355311 |
| V-13_stable            | MannKenSen (ATS)      |  0.133135   | 0.517917    |  -0.110744 |   0.406855 |
| V-13_stable            | NADA2 (R)             |  0.0712456  | 0.510925    | nan        | nan        |

## Note on NADA2 Results
The discrepancy between `MannKenSen (ATS)` and `NADA2 (R)` is expected. The NADA2 package assumes that censored values are **left-censored** (non-detects, `< Value`), whereas the data in this validation case is **right-censored** (`> Value`).
- **MannKenSen (ATS):** Correctly identifies the data as right-censored and treats `>75` as a value *greater* than 75.
- **NADA2 (R):** Interprets the censored flag as left-censoring, treating `>75` as a value *less* than 75. This artificially depresses the high values in the "Strong Increasing" scenario, resulting in a flatter slope calculation (`20.23` vs `23.83`).

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-13_strong_increasing |   0           |     0           |
| V-13_weak_decreasing   |   4.44089e-16 |    -2.22045e-13 |
| V-13_stable            |   1.73472e-18 |     1.86635e-14 |
