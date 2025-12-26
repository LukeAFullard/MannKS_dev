# Deep Diagnosis: Zero Slope in Weak Decreasing Trend

This report provides a quantitative explanation for why the "Weak Decreasing Trend" scenario (V-08) returns a Sen's slope of `0.0`, despite having a generated slope of `-0.5`.

## 1. The LWP Censoring Logic

The LWP method applies specific rules to handle slopes involving censored data. It calculates a "raw slope" using `0.5 * Limit` for left-censored values, but then forces the slope to `0` if it contradicts the censoring status:

*   **Rule 1:** Both values censored -> **Slope = 0**.
*   **Rule 2:** `LT` (Late) vs `NOT` (Early) and `Slope > 0` -> **Slope = 0**.
    *   *Logic:* You cannot conclude an increase if the series ends in a "less than" value.
*   **Rule 3:** `NOT` (Late) vs `LT` (Early) and `Slope < 0` -> **Slope = 0**.
    *   *Logic:* You cannot conclude a decrease if the series starts with a "less than" value.

## 2. The "Negative Data" Artifact

The synthetic data used for validation generated values around `-5.0`. This inadvertently exposed an artifact in the LWP heuristic.

*   **Positive Data (Standard):** `Limit = 10`. `Censored = 5 (0.5 * 10)`. Censored value is **smaller** than Limit.
*   **Negative Data (Current Case):** `Limit = -7.2`. `Censored = -3.6 (0.5 * -7.2)`.
    *   **Crucial Result:** The "Censored" value (`-3.6`) is algebraically **larger** than the Limit (`-7.2`).

This inversion caused the zeroing rules to trigger aggressively on pairs that would otherwise be valid:
*   **Rule 2 Triggered (126 times):** `NOT` (-4.3) -> `LT` (-3.6). This looks like an **increase** (Positive Slope). But since it ends in `LT`, Rule 2 forces it to `0`.
*   **Rule 3 Triggered (56 times):** `LT` (-3.6) -> `NOT` (-6.5). This looks like a **decrease** (Negative Slope). But since it starts with `LT`, Rule 3 forces it to `0`.

## 3. Quantitative Breakdown (High Noise)

We analyzed all 630 pairwise slopes for the "High Noise" scenario:

| Category | Count | Percentage |
| :--- | :--- | :--- |
| **Negative Slopes** | 287 | 45.6% |
| **Positive Slopes** | 140 | 22.2% |
| **Zero Slopes** | **203** | **32.2%** |

*   **Impact on Median:** To have a non-zero median, the "Zero" block must not overlap the 50th percentile (Rank 315). Here, the zeros occupy ranks 288 to 490. **Therefore, the median is strictly 0.**
*   **Source of Zeros:** All 203 zeros were forced by LWP rules (21 mutual, 126 Rule 2, 56 Rule 3).

## 4. Sensitivity Test (Low Noise)

To confirm the method *can* work, we ran the same setup with low noise (`0.1` vs `1.5`):
*   **Median Slope:** `-0.3756` (Correctly negative).
*   **Zero Slopes:** 224 (35.6%).
*   **Negative Slopes:** 379 (60.2%).
*   **Result:** With less noise, the "Negative" category grew large enough (60%) to push the median out of the "Zero" block.

## Conclusion

The result of `0.0` for the Weak Decreasing Trend is **not a bug**. It is the correct mathematical result of applying the LWP algorithm to this specific dataset. The result is driven by two factors:
1.  **Signal-to-Noise:** The weak trend (-0.5) was overwhelmed by noise (1.5), scattering the slopes.
2.  **LWP Heuristic on Negative Data:** The `0.5 * Value` substitution creates "larger" censored values when data is negative, causing the algorithm to flag many valid slopes as "ambiguous" (Rules 2 & 3) and force them to zero.

This confirms the `mannkensen` package accurately replicates the statistical behavior of the LWP R script, including its heuristics and edge-case behaviors.
