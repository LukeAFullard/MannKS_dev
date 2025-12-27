# Validation Report

## Plots
### V-10_strong_increasing_plot.png
![V-10_strong_increasing_plot.png](V-10_strong_increasing_plot.png)

### v10_combined.png
![v10_combined.png](v10_combined.png)

## Results
| Test ID                | Method                |     Slope |     P-Value |    Lower CI |    Upper CI |
|:-----------------------|:----------------------|----------:|------------:|------------:|------------:|
| V-10_Strong_Increasing | MannKenSen (Standard) |  2.715    | 2.82063e-12 |   2.45826   |   2.95109   |
| V-10_Strong_Increasing | MannKenSen (LWP Mode) |  2.32912  | 1.88579e-09 |   1.9529    |   2.61831   |
| V-10_Strong_Increasing | LWP-TRENDS (R)        |  2.36182  | 4.04396e-09 |   2.05494   |   2.61127   |
| V-10_Strong_Increasing | MannKenSen (ATS)      |  2.51629  | 2.82063e-12 |   2.31541   |   2.71144   |
| V-10_Strong_Increasing | NADA2 (R)             |  2.51903  | 2.82063e-12 | nan         | nan         |
| V-10_Weak_Decreasing   | MannKenSen (Standard) | -0.36556  | 0.0033235   |  -0.811011  |  -0.0614133 |
| V-10_Weak_Decreasing   | MannKenSen (LWP Mode) |  0        | 0.0569574   |  -0.160264  |   0         |
| V-10_Weak_Decreasing   | LWP-TRENDS (R)        |  0        | 0.0596148   |  -0.0990922 |   0         |
| V-10_Weak_Decreasing   | MannKenSen (ATS)      | -0.540799 | 0.0033235   |  -0.846183  |  -0.227761  |
| V-10_Weak_Decreasing   | NADA2 (R)             | -0.67191  | 0.0033235   | nan         | nan         |
| V-10_Stable            | MannKenSen (Standard) |  0.155321 | 0.462634    |  -0.138673  |   0.37226   |
| V-10_Stable            | MannKenSen (LWP Mode) |  0        | 0.281637    |   0         |   0         |
| V-10_Stable            | LWP-TRENDS (R)        |  0        | 0.151102    |   0         |   0         |
| V-10_Stable            | MannKenSen (ATS)      |  0.17667  | 0.462634    |  -0.0446432 |   0.370883  |
| V-10_Stable            | NADA2 (R)             |  0.119355 | 0.462634    | nan         | nan         |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-10_Strong_Increasing |    -0.0327024 |        -16.3512 |
| V-10_Weak_Decreasing   |     0         |         -0      |
| V-10_Stable            |     0         |          0      |
