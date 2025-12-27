# Validation Report

## Plots
### v01_combined.png
![v01_combined.png](v01_combined.png)

### v01_strong.png
![v01_strong.png](v01_strong.png)

## Results
| Test ID                | Method                |      Slope |     P-Value |    Lower CI |    Upper CI |
|:-----------------------|:----------------------|-----------:|------------:|------------:|------------:|
| V-01_strong_increasing | MannKenSen (Standard) |  1.90795   | 1.30256e-09 |   1.83378   |   1.96745   |
| V-01_strong_increasing | MannKenSen (LWP Mode) |  1.90795   | 1.30256e-09 |   1.83223   |   1.96747   |
| V-01_strong_increasing | LWP-TRENDS (R)        |  1.90795   | 1.30256e-09 |   1.84038   |   1.96027   |
| V-01_strong_increasing | MannKenSen (ATS)      |  1.90795   | 1.30256e-09 |   1.83378   |   1.96745   |
| V-01_strong_increasing | NADA2 (R)             |  1.90753   | 1.30256e-09 | nan         | nan         |
| V-01_weak_decreasing   | MannKenSen (Standard) | -0.239987  | 8.64569e-05 |  -0.31519   |  -0.149401  |
| V-01_weak_decreasing   | MannKenSen (LWP Mode) | -0.239987  | 8.64569e-05 |  -0.316845  |  -0.148377  |
| V-01_weak_decreasing   | LWP-TRENDS (R)        | -0.239987  | 8.64569e-05 |  -0.307094  |  -0.168156  |
| V-01_weak_decreasing   | MannKenSen (ATS)      | -0.239987  | 8.64569e-05 |  -0.31519   |  -0.149401  |
| V-01_weak_decreasing   | NADA2 (R)             | -0.240099  | 8.64569e-05 | nan         | nan         |
| V-01_stable            | MannKenSen (Standard) |  0.0189314 | 0.537603    |  -0.049356  |   0.095554  |
| V-01_stable            | MannKenSen (LWP Mode) |  0.0189314 | 0.537603    |  -0.0498344 |   0.0956131 |
| V-01_stable            | LWP-TRENDS (R)        |  0.0189314 | 0.537603    |  -0.0388089 |   0.081935  |
| V-01_stable            | MannKenSen (ATS)      |  0.0189314 | 0.537603    |  -0.049356  |   0.095554  |
| V-01_stable            | NADA2 (R)             |  0.0189013 | 0.537603    | nan         | nan         |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-01_strong_increasing |   0           |     0           |
| V-01_weak_decreasing   |   2.77556e-17 |    -1.38778e-14 |
| V-01_stable            |   0           |     0           |
