# Validation Report

## Plots
### v06_combined.png
![v06_combined.png](v06_combined.png)

### v06_strong.png
![v06_strong.png](v06_strong.png)

## Results
| Test ID                | Method                |      Slope |     P-Value |   Lower CI |    Upper CI |
|:-----------------------|:----------------------|-----------:|------------:|-----------:|------------:|
| V-06_strong_increasing | MannKenSen (Standard) |  2.06233   | 4.29491e-09 |   1.89825  |   2.3121    |
| V-06_strong_increasing | MannKenSen (LWP Mode) |  2.06233   | 4.29491e-09 |   1.89793  |   2.31358   |
| V-06_strong_increasing | LWP-TRENDS (R)        |  1.99704   | 9.60085e-09 |   1.93266  |   2.06203   |
| V-06_strong_increasing | MannKenSen (ATS)      |  2.06233   | 4.29491e-09 |   1.89825  |   2.3121    |
| V-06_strong_increasing | NADA2 (R)             |  2.01422   | 4.29491e-09 | nan        | nan         |
| V-06_weak_decreasing   | MannKenSen (Standard) | -0.195396  | 5.00196e-05 |  -0.270262 |  -0.131986  |
| V-06_weak_decreasing   | MannKenSen (LWP Mode) | -0.195396  | 5.00196e-05 |  -0.270388 |  -0.130297  |
| V-06_weak_decreasing   | LWP-TRENDS (R)        | -0.197641  | 5.00196e-05 |  -0.2626   |  -0.142035  |
| V-06_weak_decreasing   | MannKenSen (ATS)      | -0.195396  | 5.00196e-05 |  -0.270262 |  -0.131986  |
| V-06_weak_decreasing   | NADA2 (R)             | -0.197666  | 5.00196e-05 | nan        | nan         |
| V-06_stable            | MannKenSen (Standard) | -0.0439188 | 0.162984    |  -0.10104  |   0.0146603 |
| V-06_stable            | MannKenSen (LWP Mode) | -0.0439188 | 0.162984    |  -0.101438 |   0.0147556 |
| V-06_stable            | LWP-TRENDS (R)        | -0.0461514 | 0.162984    |  -0.101955 |   0.0102742 |
| V-06_stable            | MannKenSen (ATS)      | -0.0439188 | 0.162984    |  -0.10104  |   0.0146603 |
| V-06_stable            | NADA2 (R)             | -0.0461362 | 0.162984    | nan        | nan         |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-06_strong_increasing |    0.065293   |         3.26465 |
| V-06_weak_decreasing   |    0.00224499 |        -1.1225  |
| V-06_stable            |    0.0022326  |        -4.83756 |
