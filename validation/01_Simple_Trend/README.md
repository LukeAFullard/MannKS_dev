# Validation Report

## Plots
### v01_strong.png
![v01_strong.png](v01_strong.png)

## Results
| Test ID                | Method                |      Slope |     P-Value |    Lower CI |    Upper CI |
|:-----------------------|:----------------------|-----------:|------------:|------------:|------------:|
| V-01_strong_increasing | MannKenSen (Standard) |  1.90768   | 1.30256e-09 |   1.83378   |   1.96718   |
| V-01_strong_increasing | MannKenSen (LWP Mode) |  1.90768   | 1.30256e-09 |   1.83223   |   1.9672    |
| V-01_strong_increasing | LWP-TRENDS (R)        |  1.90795   | 1.30256e-09 |   1.84038   |   1.96027   |
| V-01_strong_increasing | MannKenSen (ATS)      |  1.90768   | 1.30256e-09 |   1.83378   |   1.96718   |
| V-01_strong_increasing | NADA2 (R)             |  1.90753   | 1.30256e-09 | nan         | nan         |
| V-01_weak_decreasing   | MannKenSen (Standard) | -0.239989  | 8.64569e-05 |  -0.315166  |  -0.149462  |
| V-01_weak_decreasing   | MannKenSen (LWP Mode) | -0.239989  | 8.64569e-05 |  -0.316826  |  -0.148426  |
| V-01_weak_decreasing   | LWP-TRENDS (R)        | -0.239987  | 8.64569e-05 |  -0.307094  |  -0.168156  |
| V-01_weak_decreasing   | MannKenSen (ATS)      | -0.239989  | 8.64569e-05 |  -0.315166  |  -0.149462  |
| V-01_weak_decreasing   | NADA2 (R)             | -0.240099  | 8.64569e-05 | nan         | nan         |
| V-01_stable            | MannKenSen (Standard) |  0.0189318 | 0.537603    |  -0.049356  |   0.095554  |
| V-01_stable            | MannKenSen (LWP Mode) |  0.0189318 | 0.537603    |  -0.0498333 |   0.0956176 |
| V-01_stable            | LWP-TRENDS (R)        |  0.0189314 | 0.537603    |  -0.0388089 |   0.081935  |
| V-01_stable            | MannKenSen (ATS)      |  0.0189318 | 0.537603    |  -0.049356  |   0.095554  |
| V-01_stable            | NADA2 (R)             |  0.0189013 | 0.537603    | nan         | nan         |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-01_strong_increasing |  -0.000267961 |      -0.0140445 |
| V-01_weak_decreasing   |  -2.45076e-06 |       0.0010212 |
| V-01_stable            |   3.76186e-07 |       0.0019871 |
