# Validation Report


**V-14: Monthly Seasonal Trend**

This test verifies the seasonal trend analysis functionality on a simple monthly dataset.
It compares the standard `mannkensen` seasonal test against the LWP-TRENDS R script and NADA2.

**Scenarios:**
1.  **Strong Increasing:** Clear positive trend with seasonality.
2.  **Weak Decreasing:** Subtle negative trend with seasonality.
3.  **Stable:** No underlying trend, just seasonality.


## Plots
### V14_Trend_Analysis.png
![V14_Trend_Analysis.png](V14_Trend_Analysis.png)

## Results
| Test ID                | Method                |        Slope |     P-Value |    Lower CI |    Upper CI |
|:-----------------------|:----------------------|-------------:|------------:|------------:|------------:|
| V-14_strong_increasing | MannKenSen (Standard) |  2.00497     | 0           |   1.94106   |   2.08928   |
| V-14_strong_increasing | MannKenSen (LWP Mode) |  2.00497     | 0           |   1.94112   |   2.08923   |
| V-14_strong_increasing | LWP-TRENDS (R)        |  2.00497     | 3.72242e-39 |   1.9468    |   2.07599   |
| V-14_strong_increasing | MannKenSen (ATS)      |  2.00522     | 0           |   1.98773   |   2.03538   |
| V-14_strong_increasing | NADA2 (R)             |  1.902       | 0.002       | nan         | nan         |
| V-14_weak_decreasing   | MannKenSen (Standard) | -0.566635    | 3.76987e-12 |  -0.704278  |  -0.412259  |
| V-14_weak_decreasing   | MannKenSen (LWP Mode) | -0.566635    | 3.76987e-12 |  -0.704155  |  -0.412702  |
| V-14_weak_decreasing   | LWP-TRENDS (R)        | -0.566635    | 3.76988e-12 |  -0.668577  |  -0.435515  |
| V-14_weak_decreasing   | MannKenSen (ATS)      | -0.566463    | 3.76987e-12 |  -0.600073  |  -0.531601  |
| V-14_weak_decreasing   | NADA2 (R)             | -0.6906      | 0.002       | nan         | nan         |
| V-14_stable            | MannKenSen (Standard) |  0.000520175 | 0.979401    |  -0.0859605 |   0.0802783 |
| V-14_stable            | MannKenSen (LWP Mode) |  0.000520175 | 0.979401    |  -0.0855397 |   0.0800738 |
| V-14_stable            | LWP-TRENDS (R)        |  0.000520175 | 0.979401    |  -0.0535041 |   0.0633387 |
| V-14_stable            | MannKenSen (ATS)      |  0.00051967  | 0.979401    |  -0.0210754 |   0.0294619 |
| V-14_stable            | NADA2 (R)             | -0.08904     | 0.974       | nan         | nan         |

## LWP Accuracy (Python vs R)
| Test ID                |   Slope Error |   Slope % Error |
|:-----------------------|--------------:|----------------:|
| V-14_strong_increasing |    0          |      0          |
| V-14_weak_decreasing   |    0          |     -0          |
| V-14_stable            |   -1.0842e-19 |     -2.0843e-14 |
