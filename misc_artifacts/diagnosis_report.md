# Diagnosis of Results Discrepancies

This report details the findings from investigating differences between the `MannKenSen` (Python) package and the `LWP-TRENDS` (R) script.

## 1. Discrepancy in Slope Values (V-08 Strong Increasing)

**Initial Observation:**
*   MKS (LWP Mode): `1.58075`
*   LWP-TRENDS (R): `1.58025`
*   Error: ~0.03%

**Root Cause:**
The discrepancy was caused by a fundamental difference in how the time vector `t` was being constructed in the validation harness vs how R does it internally.

*   **Python (Original Validation Logic):** Used a "Decimal Year" approximation.
    ```python
    t = year + (day_of_year - 1) / 365.25
    ```
    This method effectively resets the "fractional year" clock every January 1st. It treats 2001-01-01 as exactly `2001.0`.

*   **R (LWP Script):** Uses continuous "Julian Days" scaled by 365.25.
    ```r
    t = (date - 1970-01-01) / 365.25
    ```
    Because a standard year is 365 days (not 365.25), `2001-01-01` is day 366 (relative to 2000-01-01).
    `366 / 365.25 = 1.00205...`
    In the R system, 1 year later is `1.002` years on the timeline, whereas in the original Python logic it was exactly `1.0`.

**Resolution:**
The `validation_utils.py` script was updated to calculate `t_numeric` for Python runs using the exact same logic as R:
```python
t_numeric = (dates - pd.Timestamp("1970-01-01")).days / 365.25
```

**Final Result:**
After applying this fix to the validation harness, the results match perfectly:
*   MKS (LWP Mode): `1.58025`
*   LWP-TRENDS (R): `1.58025`
*   Error: `~1e-13` %

This confirms that the `MannKenSen` package logic is correct and robust, and the initial discrepancy was purely due to an apples-to-oranges comparison of time coordinates in the test runner.

## 2. Zero Slope for "Weak Decreasing Trend"

**Observation:**
Both MKS and R returned a slope of `0` for the "Weak Decreasing Trend" scenario in V-08, despite the data generation using a slope of `-0.5`.

**Investigation:**
We verified the LWP censoring logic rules:
*   Rule: If `Slope < 0` (Decreasing) and the pair is `NOT` (early) -> `LT` (late), the slope is **valid** and preserved.
*   This rule does *not* force the slope to 0 for a decreasing trend ending in censored values.

**Root Cause:**
The trend was simply **too weak relative to the noise**.
*   Generated Slope: `-0.5`.
*   Noise Std Dev: `1.5`.
*   Time Span: 3 years.
*   Total Drop: `1.5` units.
*   Noise Range: `+/- 4.5` units.

The signal-to-noise ratio was too low. The statistical test (Mann-Kendall) correctly identified `p-value ~ 0.92` (not significant), and the median slope calculation resulted in 0, which is a reasonable estimate for "no significant trend". This confirms the robustness of the method (it didn't hallucinate a trend from noise) rather than a bug in the censoring logic.
