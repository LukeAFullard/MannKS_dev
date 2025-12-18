# Audit Findings: LWP-TRENDS R vs. MannKenSen Python

This document outlines the key methodological differences between the LWP-TRENDS R script (`LWPTrends_v2502.r`) and the `MannKenSen` Python package. These are areas where the Python implementation will produce different results from the R script, even when using all available LWP-compatibility flags.

The goal of this audit is to provide transparency and a clear validation story for the package.

---

### 1. Time Vector Ranking and Tie Handling in the Mann-Kendall Test

While both implementations use ranks for the time vector in the Mann-Kendall test, the method of ranking differs significantly, which impacts the handling of ties and the final variance calculation.

-   **LWP-TRENDS (R):** Creates a **categorical label** for each observation by combining its "Season" and "Year" (e.g., "Jan-2001"). It then ranks these labels. As a result, all observations within the same season-year period are assigned the **same rank**, creating a large group of ties in the time vector.
-   **MannKenSen (Python):** Ranks the **numeric timestamps** directly using `scipy.stats.rankdata(t, method='ordinal')`. This method assigns a unique rank to each observation unless the timestamps are numerically identical down to the floating-point precision.

**Reason & Impact:**
The Python approach provides a higher-resolution ranking of the observation times. The R script's method introduces a significant number of ties into the time vector whenever there is more than one observation per season-year period.

Because the Mann-Kendall variance calculation is sensitive to ties, this fundamental difference in ranking methodology will cause the following outputs to diverge whenever data is sampled more frequently than the Season-Year interval:
-   `var_s` (Variance of S)
-   `z` (Z-score)
-   `p` (p-value)

---

### 2. Confidence Interval Calculation Method

The two libraries use different default methods for determining the confidence intervals from the list of slopes.

-   **LWP-TRENDS (R):** Calculates the ranks for the lower and upper confidence limits as floating-point numbers. It then uses R's `approx` function (linear interpolation) to find the slope values corresponding to these fractional ranks.
-   **MannKenSen (Python):** The default method (`ci_method='direct'`) calculates the ranks as floating-point numbers and then **rounds** them to the nearest integer to use as direct array indices.

**Reason & Impact:**
The Python default is a direct indexing method, which is simpler and avoids interpolation. However, it is a different statistical approach. To replicate the R script's behavior, the user **must** specify `ci_method='lwp'`. If they do not, the `lower_ci` and `upper_ci` outputs will likely differ.

---

### 3. Trend Classification Parameterization

The final trend classification (e.g., "Increasing", "No Trend") depends on a significance level, which is handled differently.

-   **LWP-TRENDS (R):** The `AssignConfCat` function, used for classification, appears to use a **hardcoded significance level** (likely 0.05) and does not offer a parameter to adjust it.
-   **MannKenSen (Python):** The classification is determined by the user-provided `alpha` parameter (defaulting to 0.05), which offers greater flexibility.

**Reason & Impact:**
Our implementation provides more control to the user. However, if a user runs a trend test with an `alpha` value other than the R script's hardcoded default, the final `classification` output may differ even if the underlying p-value were the same.

---

### 4. Handling of Right-Censored Data in the Mann-Kendall Test

The two libraries have different default methods for handling right-censored (`>`) data during the Mann-Kendall test.

-   **LWP-TRENDS (R):** In the `GetKendal` function, it performs a specific pre-processing step: it finds the maximum right-censored value, adds 0.1, and replaces *all* right-censored values with this new single value. This treats them as a large group of tied, non-censored observations.
-   **MannKenSen (Python):** The default method (`mk_test_method='robust'`) is a non-parametric approach that does not modify the underlying data values. The R script's heuristic behavior can be replicated, but only if the user explicitly specifies `mk_test_method='lwp'`.

**Reason & Impact:**
The Python default is a more statistically standard and robust method. The `'lwp'` method is provided for backward compatibility. If a user has right-censored data and does not set `mk_test_method='lwp'`, the `s`, `var_s`, and `p` values will differ significantly from the R script.

---

### 5. Sen's Slope Calculation with Censored Data

This is a subtle but important distinction in how ambiguous slopes are handled.

-   **LWP-TRENDS (R):** When calculating the slope between pairs of points where the direction is ambiguous (e.g., between two left-censored values, or between a non-censored value and a left-censored value that is higher), the script sets the slope for that pair to **0**.
-   **MannKenSen (Python):** This "set to 0" behavior is replicated only when the user specifies `sens_slope_method='lwp'`. The default Python behavior (`sens_slope_method='nan'`) is to set these ambiguous slopes to `np.nan`, effectively removing them from the median calculation.

**Reason & Impact:**
The Python default (`'nan'`) is more statistically neutral, as it does not bias the median slope towards zero. The `'lwp'` method is provided for backward compatibility. If a user has censored data and does not set `sens_slope_method='lwp'`, the final `slope` will likely differ from the R script.
