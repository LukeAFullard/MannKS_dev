# Validation Report

## Plots
### V-10_strong_increasing_plot.png
![V-10_strong_increasing_plot.png](V-10_strong_increasing_plot.png)

## Results
| Test ID                | Method                |      Slope |     P-Value |   Lower CI |   Upper CI |
|:-----------------------|:----------------------|-----------:|------------:|-----------:|-----------:|
| V-10_Strong_Increasing | MannKenSen (Standard) |  2.71512   | 2.82063e-12 |   2.4573   |   2.94955  |
| V-10_Strong_Increasing | MannKenSen (LWP Mode) |  2.32861   | 1.88579e-09 |   1.95259  |   2.61465  |
| V-10_Strong_Increasing | LWP-TRENDS (R)        |  2.36182   | 4.04396e-09 |   2.05494  |   2.61127  |
| V-10_Strong_Increasing | MannKenSen (ATS)      |  2.51502   | 2.82063e-12 |   2.3146   |   2.70217  |
| V-10_Strong_Increasing | NADA2 (R)             |  2.51903   | 2.82063e-12 | nan        | nan        |
| V-10_Weak_Decreasing   | MannKenSen (Standard) | -0.433261  | 0.0152008   |  -0.786362 |  -0.114973 |
| V-10_Weak_Decreasing   | MannKenSen (LWP Mode) |  0         | 0.0535885   |  -0.268971 |   0        |
| V-10_Weak_Decreasing   | LWP-TRENDS (R)        |  0         | 0.0796326   |  -0.178919 |   0        |
| V-10_Weak_Decreasing   | MannKenSen (ATS)      | -0.48117   | 0.0152008   |  -0.753334 |  -0.200442 |
| V-10_Weak_Decreasing   | NADA2 (R)             | -0.47439   | 0.0152008   | nan        | nan        |
| V-10_Stable            | MannKenSen (Standard) |  0.0812514 | 0.557125    |  -0.138549 |   0.292511 |
| V-10_Stable            | MannKenSen (LWP Mode) |  0         | 0.457183    |   0        |   0        |
| V-10_Stable            | LWP-TRENDS (R)        |  0         | 0.353063    |   0        |   0        |
| V-10_Stable            | MannKenSen (ATS)      |  0.0812514 | 0.557125    |  -0.100061 |   0.257235 |
| V-10_Stable            | NADA2 (R)             |  0.0855787 | 0.557125    | nan        | nan        |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-10_Strong_Increasing |    -0.0332163 |        -16.6082 |
| V-10_Weak_Decreasing   |     0         |         -0      |
| V-10_Stable            |     0         |          0      |

## Analysis of Zero Slopes in LWP Mode

A key observation from the results above is that the **LWP Mode** (and the matching R script) produces a Sen's slope of exactly `0` for the "Weak Decreasing" and "Stable" scenarios, while the standard methods return non-zero values.

This is **not a bug** but a consequence of the LWP methodology for censored data. When calculating the Sen's slope, the LWP algorithm handles "ambiguous" slopes (e.g., between two censored values like `<2` and `<2`, or a censored vs. non-censored pair where the direction is uncertain) by forcing them to `0`.

In scenarios with weak trends and significant censoring (like these, with 30% mixed censoring), a large proportion of pairwise slopes are ambiguous. This creates a strong "attractor" at zero. If the number of ambiguous pairs is high enough, the median of all pairwise slopes becomes exactly zero. This effectively biases the result towards "no trend" when the signal-to-noise ratio is low and censoring is present. The standard MannKenSen method and ATS do not use this zero-forcing heuristic, allowing them to estimate the subtle slopes more naturally.
