# V-12: Sen's Slope Censored Multipliers

## Objective
Isolate and verify the effect of the `lt_mult` and `gt_mult` parameters. The test uses data with **multiple censoring levels** (<1, <3, <5) to ensure robust validation of multiplier application across different limits.

## Trend Plot (Strong Increasing)

![Trend Plot](plot_trend.png)

## Validation Results
| Test ID                | Method                |    Slope |    P-Value |   Lower CI |   Upper CI |
|:-----------------------|:----------------------|---------:|-----------:|-----------:|-----------:|
| V-12_strong_increasing | MannKenSen (Standard) |  4.9797  | 5.6335e-08 |     4.5448 |    5.5037  |
| V-12_strong_increasing | MannKenSen (LWP Mode) |  4.7301  | 5.6335e-08 |     4.2837 |    5.178   |
| V-12_strong_increasing | LWP-TRENDS (R)        |  4.7301  | 5.5438e-08 |     4.3619 |    5.1169  |
| V-12_strong_increasing | MannKenSen (ATS)      |  4.8143  | 5.6335e-08 |     4.4418 |    5.1804  |
| V-12_strong_increasing | NADA2 (R)             |  7.6422  | 5.5438e-08 |   nan      |  nan       |
| V-12_weak_decreasing   | MannKenSen (Standard) | -3.504   | 2.8289e-05 |    -4.0588 |   -2.9523  |
| V-12_weak_decreasing   | MannKenSen (LWP Mode) | -2.8983  | 2.8289e-05 |    -3.4019 |    0       |
| V-12_weak_decreasing   | LWP-TRENDS (R)        | -2.8983  | 2.6147e-05 |    -3.3193 |   -1.4826  |
| V-12_weak_decreasing   | MannKenSen (ATS)      | -3.1559  | 2.8289e-05 |    -3.6091 |   -2.7529  |
| V-12_weak_decreasing   | NADA2 (R)             | -5.2501  | 2.6147e-05 |   nan      |  nan       |
| V-12_stable            | MannKenSen (Standard) | -0.90411 | 0.54547    |    -6.1627 |    4.6766  |
| V-12_stable            | MannKenSen (LWP Mode) |  0       | 0.54547    |     0      |    0       |
| V-12_stable            | LWP-TRENDS (R)        |  0       | 0.53444    |     0      |    0       |
| V-12_stable            | MannKenSen (ATS)      | -0.66991 | 0.54547    |    -2.1226 |    0.77514 |
| V-12_stable            | NADA2 (R)             | -0.63946 | 0.53444    |   nan      |  nan       |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-12_strong_increasing |    0          |      0          |
| V-12_weak_decreasing   |    4.4409e-16 |      1.5322e-14 |
| V-12_stable            |  nan          |    nan          |
### Multiplier Sensitivity (Weak Decreasing Scenario)
Demonstrating the effect of changing `lt_mult` on the Sen's Slope.

| lt_mult | Slope (units/year) | P-Value |
| :--- | :--- | :--- |
| 0.2 | -3.79574 | 0.00003 |
| 0.5 | -3.50399 | 0.00003 |
| 0.8 | -2.95458 | 0.00003 |
