# Validation Report


**V-05: Unequally Spaced Time Series**

*   **Objective:** Verify a core feature of `mannkensen` on a non-seasonal, unequally spaced time series.
*   **Data Description:** Data with a clear trend but with random, non-uniform time gaps between samples. This test highlights a key methodological difference where the R script is expected to differ.


## Plots
### v05_combined.png
![v05_combined.png](v05_combined.png)

### v05_strong.png
![v05_strong.png](v05_strong.png)

## Results
| Test ID                | Method                |     Slope |     P-Value |    Lower CI |     Upper CI |
|:-----------------------|:----------------------|----------:|------------:|------------:|-------------:|
| V-05_strong_increasing | MannKenSen (Standard) |  2.00218  | 8.67976e-10 |   1.96823   |   2.04047    |
| V-05_strong_increasing | MannKenSen (LWP Mode) |  2.00218  | 8.67976e-10 |   1.9682    |   2.04071    |
| V-05_strong_increasing | LWP-TRENDS (R)        |  2.00218  | 8.67976e-10 |   1.97451   |   2.0295     |
| V-05_strong_increasing | MannKenSen (ATS)      |  2.00218  | 8.67976e-10 |   1.96823   |   2.04047    |
| V-05_strong_increasing | NADA2 (R)             |  2.00196  | 8.67976e-10 | nan         | nan          |
| V-05_weak_decreasing   | MannKenSen (Standard) | -0.214903 | 9.6283e-07  |  -0.257443  |  -0.172092   |
| V-05_weak_decreasing   | MannKenSen (LWP Mode) | -0.214903 | 9.6283e-07  |  -0.257452  |  -0.172062   |
| V-05_weak_decreasing   | LWP-TRENDS (R)        | -0.214903 | 9.6283e-07  |  -0.247672  |  -0.180224   |
| V-05_weak_decreasing   | MannKenSen (ATS)      | -0.214903 | 9.6283e-07  |  -0.257443  |  -0.172092   |
| V-05_weak_decreasing   | NADA2 (R)             | -0.214935 | 9.6283e-07  | nan         | nan          |
| V-05_stable            | MannKenSen (Standard) | -0.024693 | 0.229969    |  -0.0619147 |   0.014306   |
| V-05_stable            | MannKenSen (LWP Mode) | -0.024693 | 0.229969    |  -0.0620224 |   0.0143121  |
| V-05_stable            | LWP-TRENDS (R)        | -0.024693 | 0.229969    |  -0.0519878 |   0.00691853 |
| V-05_stable            | MannKenSen (ATS)      | -0.024693 | 0.229969    |  -0.0619147 |   0.014306   |
| V-05_stable            | NADA2 (R)             | -0.02468  | 0.229969    | nan         | nan          |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-05_strong_increasing |  -4.44089e-16 |    -2.22045e-14 |
| V-05_weak_decreasing   |   0           |    -0           |
| V-05_stable            |  -1.04083e-17 |     4.2151e-14  |
