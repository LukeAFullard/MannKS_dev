# Validation Report


    # V-08: Left-Censored Trend

    This validation case tests the package's ability to handle left-censored data (values reported as less than a detection limit, e.g., `<5.0`).

    Three scenarios were tested with updated parameters to ensure robust detectability:
    1. **Strong Increasing Trend**: Slope 5.0, Noise 1.0. Clear positive trend.
    2. **Weak Decreasing Trend**: Slope -0.8, Noise 0.5. Detectable negative trend (avoiding zero-slope artifacts from high noise).
    3. **Stable (No Trend)**: Slope 0.0, Noise 1.0. No underlying trend.

    Comparison is made between:
    - **MannKenSen (Standard)**: Uses the 'robust' method for Mann-Kendall and Sen's slope.
    - **MannKenSen (LWP Mode)**: Uses `mk_test_method='lwp'` and `agg_method='lwp'` to mimic R.
    - **LWP-TRENDS R Script**: The reference implementation.
    - **MannKenSen (ATS)**: Uses the Akritas-Theil-Sen estimator.
    - **NADA2 R Script**: Using the ATS estimator (reference for ATS mode).


## Plots
### v08_strong_left_censored.png
![v08_strong_left_censored.png](v08_strong_left_censored.png)

## Results
| Test ID                | Method                |     Slope |     P-Value |   Lower CI |    Upper CI |
|:-----------------------|:----------------------|----------:|------------:|-----------:|------------:|
| V-08_strong_increasing | MannKenSen (Standard) |  4.47218  | 1.4011e-13  |   4.05295  |   4.86053   |
| V-08_strong_increasing | MannKenSen (LWP Mode) |  4.47218  | 1.4011e-13  |   4.0538   |   4.86051   |
| V-08_strong_increasing | LWP-TRENDS (R)        |  4.47218  | 9.96371e-14 |   4.14945  |   4.76648   |
| V-08_strong_increasing | MannKenSen (ATS)      |  4.47218  | 1.4011e-13  |   4.05295  |   4.86053   |
| V-08_strong_increasing | NADA2 (R)             |  4.47568  | 9.9698e-14  | nan        | nan         |
| V-08_weak_decreasing   | MannKenSen (Standard) | -0.632335 | 1.35471e-07 |  -0.803496 |  -0.444226  |
| V-08_weak_decreasing   | MannKenSen (LWP Mode) | -0.632335 | 1.35471e-07 |  -0.803462 |  -0.444413  |
| V-08_weak_decreasing   | LWP-TRENDS (R)        | -0.632335 | 1.13587e-07 |  -0.781558 |  -0.497372  |
| V-08_weak_decreasing   | MannKenSen (ATS)      | -0.632335 | 1.35471e-07 |  -0.803496 |  -0.444226  |
| V-08_weak_decreasing   | NADA2 (R)             | -0.633091 | 1.13587e-07 | nan        | nan         |
| V-08_stable            | MannKenSen (Standard) | -0.212139 | 0.258251    |  -0.652316 |   0.118085  |
| V-08_stable            | MannKenSen (LWP Mode) | -0.212139 | 0.258251    |  -0.652182 |   0.117991  |
| V-08_stable            | LWP-TRENDS (R)        | -0.212139 | 0.255351    |  -0.580777 |   0.0503089 |
| V-08_stable            | MannKenSen (ATS)      | -0.212139 | 0.258251    |  -0.652316 |   0.118085  |
| V-08_stable            | NADA2 (R)             | -0.212171 | 0.255351    | nan        | nan         |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-08_strong_increasing |  -3.55271e-15 |    -7.10543e-14 |
| V-08_weak_decreasing   |   4.44089e-16 |    -5.55112e-14 |
| V-08_stable            |  -1.66533e-16 |     7.85021e-14 |
