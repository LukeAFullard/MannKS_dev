# Validation Report


**V-18: Seasonal Data with Missing Seasons**

This test verifies the seasonal trend analysis when entire seasons are missing from the dataset.
Specifically, all data for **July (Month 7)** and **August (Month 8)** will be removed.
This forces the test to skip these seasons and only analyze the remaining 10 months.

**Note:** The LWP-TRENDS R script has a known fragility with missing seasons and may fail to run.
The `mannkensen` package is expected to handle this gracefully by skipping the missing seasons and analyzing the rest.


## Plots
### V18_Missing_Seasons_Analysis.png
![V18_Missing_Seasons_Analysis.png](V18_Missing_Seasons_Analysis.png)

## Results
| Test ID                | Method                |        Slope |      P-Value |      Lower CI |      Upper CI |
|:-----------------------|:----------------------|-------------:|-------------:|--------------:|--------------:|
| V-18_strong_increasing | MannKenSen (Standard) |  2.00924     |  0           |   1.94571     |   2.10345     |
| V-18_strong_increasing | MannKenSen (LWP Mode) |  2.00924     |  0           |   1.94597     |   2.10332     |
| V-18_strong_increasing | LWP-TRENDS (R)        | -2.14748e+09 | -2.14748e+09 |  -2.14748e+09 |  -2.14748e+09 |
| V-18_strong_increasing | MannKenSen (ATS)      |  2.00947     |  0           |   1.98842     |   2.03036     |
| V-18_strong_increasing | NADA2 (R)             |  1.977       |  0.002       | nan           | nan           |
| V-18_weak_decreasing   | MannKenSen (Standard) | -0.504437    |  4.08293e-10 |  -0.65835     |  -0.354837    |
| V-18_weak_decreasing   | MannKenSen (LWP Mode) | -0.504437    |  4.08293e-10 |  -0.655193    |  -0.356238    |
| V-18_weak_decreasing   | LWP-TRENDS (R)        | -2.14748e+09 | -2.14748e+09 |  -2.14748e+09 |  -2.14748e+09 |
| V-18_weak_decreasing   | MannKenSen (ATS)      | -0.504562    |  4.08293e-10 |  -0.55313     |  -0.471303    |
| V-18_weak_decreasing   | NADA2 (R)             | -0.5652      |  0.002       | nan           | nan           |
| V-18_stable            | MannKenSen (Standard) | -0.0463638   |  0.350623    |  -0.114749    |   0.0449356   |
| V-18_stable            | MannKenSen (LWP Mode) | -0.0463638   |  0.350623    |  -0.113451    |   0.0447268   |
| V-18_stable            | LWP-TRENDS (R)        | -2.14748e+09 | -2.14748e+09 |  -2.14748e+09 |  -2.14748e+09 |
| V-18_stable            | MannKenSen (ATS)      | -0.0466262   |  0.350623    |  -0.0774927   |  -0.0233403   |
| V-18_stable            | NADA2 (R)             | -0.1062      |  0.354       | nan           | nan           |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-18_strong_increasing |   2.14748e+09 |     1.07374e+11 |
| V-18_weak_decreasing   |   2.14748e+09 |    -4.29497e+11 |
| V-18_stable            |   2.14748e+09 |  -100           |
