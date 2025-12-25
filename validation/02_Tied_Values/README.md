# Validation Report

## Plots
### v02_strong.png
![v02_strong.png](v02_strong.png)

## Results
| Test ID                     | Method                |       Slope |     P-Value |   Lower CI |   Upper CI |
|:----------------------------|:----------------------|------------:|------------:|-----------:|-----------:|
| V-02_strong_increasing_tied | MannKenSen (Standard) | 1.20247     | 5.77838e-09 |   0.857898 |    1.54808 |
| V-02_strong_increasing_tied | MannKenSen (LWP Mode) | 1.20247     | 5.77838e-09 |   0.857898 |    1.54765 |
| V-02_strong_increasing_tied | LWP-TRENDS (R)        | 1.20148     | 1.97418e-09 |   0.94076  |    1.49693 |
| V-02_strong_increasing_tied | MannKenSen (ATS)      | 1.20247     | 5.77838e-09 |   0.857898 |    1.54808 |
| V-02_strong_increasing_tied | NADA2 (R)             | 1.20247     | 1.97418e-09 | nan        |  nan       |
| V-02_weak_decreasing_tied   | MannKenSen (Standard) | 0           | 0.00104451  |  -0.82589  |    0       |
| V-02_weak_decreasing_tied   | MannKenSen (LWP Mode) | 0           | 0.00104451  |  -0.817379 |    0       |
| V-02_weak_decreasing_tied   | LWP-TRENDS (R)        | 0           | 0.000458025 |  -0.72759  |    0       |
| V-02_weak_decreasing_tied   | MannKenSen (ATS)      | 0           | 0.00104451  |  -0.82589  |    0       |
| V-02_weak_decreasing_tied   | NADA2 (R)             | 3.61818e-08 | 0.000458025 | nan        |  nan       |
| V-02_stable_tied            | MannKenSen (Standard) | 0           | 0.27264     |   0        |    0       |
| V-02_stable_tied            | MannKenSen (LWP Mode) | 0           | 0.27264     |   0        |    0       |
| V-02_stable_tied            | LWP-TRENDS (R)        | 0           | 0.164306    |   0        |    0       |
| V-02_stable_tied            | MannKenSen (ATS)      | 0           | 0.27264     |   0        |    0       |
| V-02_stable_tied            | NADA2 (R)             | 2.75103e-08 | 0.164306    | nan        |  nan       |

## LWP Accuracy (Python vs R)
| Test ID                     |   Slope Error |   Slope % Error |
|:----------------------------|--------------:|----------------:|
| V-02_strong_increasing_tied |   0.000988873 |       0.0824061 |
| V-02_weak_decreasing_tied   |   0           |      -0         |
| V-02_stable_tied            |   0           |       0         |
