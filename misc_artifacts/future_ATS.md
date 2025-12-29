# Using `cenken` / `censeaken` (Akritas–Theil–Sen) for trend **magnitude** — full report and Python implementation

**Purpose:** give you everything you need to (1) understand how `cenken` / `censeaken` compute a Theil–Sen style slope for censored data (the Akritas–Theil–Sen (ATS) estimator), (2) understand how that differs from the LWP implementation, and (3) implement a working ATS estimator (plus seasonal variant and bootstrap CIs) in **Python** for use in your package, *with logic that accurately reflects the reference R implementation*.

This is a single self-contained Markdown file. Key references are cited inline.

---

## Executive summary

* `cenken` / `censeaken` implement the **Akritas–Theil–Sen (ATS)** approach: they *directly work with censoring* (intervals) and compute a slope by inverting a censored Kendall statistic (i.e. finding the slope `β` that makes the Kendall-type `S` (or τ) of residuals equal to zero). The intercept is estimated nonparametrically using a **Turnbull estimator** on the residuals. This is a *formal censored-data* extension of Theil–Sen. ([pure.psu.edu][1])

* LWP-Trends uses Helsel-style censored **Kendall** logic for the trend **test** (so trend direction / p-values are compatible with NADA), **but** for slope it uses a *pragmatic substitution* rule — left-censored values replaced by `LOD * 0.5` and right-censored by `LOD * 1.1` and then a standard Theil–Sen on those substituted values. That is **not** the ATS estimator; it is a pragmatic heuristic that is defensible under light censoring but can be biased as censoring grows. 

* The `censeaken` script for seasonal trends calculates the overall trend **slope and intercept** by applying the non-seasonal ATS method (`cenken`) to the **entire dataset at once**. Per-season trends are calculated for reporting, and the overall *p-value* is derived from a separate permutation test on the sum of seasonal statistics.

* This report explains ATS theory, shows how it differs from LWP, and supplies Python code to compute:

  * ATS slope (root-finding on censored-Kendall `S(β)`)
  * A robust intercept using a pragmatic implementation of the Turnbull estimator logic.
  * bootstrap confidence intervals
  * A **Stratified ATS** approach for seasonal data, which improves upon the `censeaken` methodology by strictly enforcing seasonal boundaries during slope calculation.
  * diagnostics (percent censored, % of pairwise slopes that involved censored intervals, warnings)

Key academic sources: Akritas et al. (1995) for ATS, Turnbull (1976) for interval- / Turnbull-logic, Helsel for survival/ROS guidance and tie rules; NADA / NADA2 document the R functions (`cenken`, `censeaken`) that implement ATS. ([pure.psu.edu][1])

---

## 1. Conceptual background (quick)

* **Theil–Sen (uncensored)**: slope = median of slopes computed from all point-pairs `s_ij = (y_j - y_i)/(x_j - x_i)`. Equivalently, Sen slope is the slope `β` that makes Kendall's τ between `x` and residuals `r = y - β x` ≈ 0. (This equivalence is what Akritas leverages.) ([Wikipedia][2])

* **Censoring**: an observation may be left-censored (`y < LOD`), right-censored (`y > U`), or exact. Each observation becomes an **interval**: `[lower_i, upper_i]` where lower_i = upper_i = y_i for detected observations; lower=-∞/upper=LOD for left-censor; vice versa for right-censor. Turnbull's estimator is the canonical nonparametric method for interval-censored distributions. ([JSTOR][3])

* **Akritas–Theil–Sen (ATS)**: extend the Theil–Sen idea by working on **residual intervals** `R_i(β) = [lower_i - β x_i, upper_i - β x_i]`. For a candidate slope `β` we compare pairs of residual intervals (`R_i(β)` vs `R_j(β)`). If intervals are **disjoint** we can definitively say `r_i > r_j` or `r_i < r_j`; if they overlap we treat as a tie / indeterminate. Use these pairwise comparisons to compute a censored Kendall `S(β)` (concordant − discordant). ATS finds the `β` such that `S(β) = 0` (or equivalently τ ≈ 0). The intercept is then estimated (e.g. using Turnbull median of residuals) so the line passes through the data in the censored sense. The Akritas paper gives asymptotic variance formulae and shows the method works under mild conditions. ([pure.psu.edu][1])

* **`censeaken` / `cenken` (R / NADA2)** implement ATS for singly- or doubly-censored data and a seasonal variant. `censeaken` performs seasonal ATS per-season and combines (per-season S and variance) to get the overall test; slope calculation follows the ATS logic. See NADA / NADA2 docs. ([rdocumentation.org][4])

---

## 2. How LWP differs (short, precise)

* **Kendall trend test:** LWP adopts Helsel tie rules for the Mann–Kendall test — i.e., censored pairs which can be resolved count as concordant/discordant, otherwise ties. This part *matches* NADA behavior. 

* **Sen slope (magnitude):** LWP **does not implement ATS**. Instead they replace:

  * left-censored values `y < LOD` by `LOD * 0.5`
  * right-censored values `y > U` by `U * 1.1`
    and then compute a **standard Theil–Sen** slope on these substituted numeric values (with some tie-handling rules). This is a pragmatic shortcut: it is fast and “works” when censoring is light (<~15%) but is *not* a formally consistent censored estimator in general. LWP documents the heuristic and warns when many censored values are present. 

**Implication:** the ATS-based slope and the LWP substituted-Theil–Sen slope will usually agree for low censoring but can diverge (sometimes substantially) when detection limits are frequent, multiple LODs appear, or censoring is non-random. Use ATS for statistical correctness; use LWP’s approach for fast operational routines where you accept approximations and have light censoring. ([rdocumentation.org][4])

---

## 3. Algorithmic description of ATS (how `cenken` works, at high level)

1. Represent each observation `i` as an interval `[a_i, b_i]`:

   * detected: `a_i = b_i = y_i`
   * left-censored: `a_i = -∞`, `b_i = LOD_i` (use a large negative sentinel in practice)
   * right-censored: `a_i = U_i`, `b_i = +∞` (use a large positive sentinel in practice)
     (If you prefer, flip left-censor to right-censor via `-y` trick — NADA sometimes uses that.) ([cran.r-project.org][5])

2. For a candidate slope `β`, compute **residual intervals**

   ```
   R_i(β) = [a_i - β*x_i, b_i - β*x_i]
   ```

   (here `x_i` = time or covariate).

3. For each pair `i < j` compare `R_i(β)` and `R_j(β)`:

   * If `min(R_i) > max(R_j)` → `r_i > r_j` (concordant)
   * Else if `max(R_i) < min(R_j)` → `r_i < r_j` (discordant)
   * Else → tie (indeterminate)
     Count `S(β) = #concordant − #discordant`.

4. Find `β*` such that `S(β*) = 0`. `S(β)` is a (piecewise) monotonic function in `β` and Akritas gives conditions for root-finding (practically one uses bisection/search over an interval of plausible slopes). `β*` is the ATS slope.

5. **Intercept**: The `cenken` script uses a **Turnbull estimator** to find the median of the residual intervals `R_i(β*)`. This is a formal non-parametric method for finding the empirical distribution of interval-censored data. It uses an iterative Expectation-Maximization (EM) algorithm to assign probability masses to the gaps between interval endpoints. From the resulting empirical cumulative distribution function (ECDF), the median (50th percentile) is found. This is statistically robust and correctly handles the uncertainty from censored values.

6. Variance / CI: Akritas supplies an asymptotic variance formula (nontrivial). Practically, many implementations (and this report's code) compute bootstrap confidence intervals (resampling preserving censoring patterns) as a robust alternative.

---

## 4. Implementation plan in Python (practical choices & trade-offs)

**Design goals**

* Accurate ATS slope for singly left-censored (typical) or mixed censoring.
* Clear diagnostics (prop censored, pairwise tie fraction).
* Reasonable performance for `n` up to a few hundreds (O(n²) pairwise comparisons is typical).
* Bootstrap CIs implemented (respects censoring).
* A seasonal variant that correctly mirrors the `censeaken` R script's logic.

**Trade-offs**

* A full, production-grade implementation of the Turnbull EM algorithm is complex. We provide a pragmatic but robust Python function that correctly implements the core logic of finding the median from an ECDF derived from interval data. This is much more accurate than a simple heuristic and sufficient for this application.
* For very large `n`, we'd recommend faster Theil–Sen algorithms adapted for interval comparisons — but for environmental monitoring (n typically 50–500) O(n²) is fine.

---

## 5. Python code (complete, runnable)

> This code is written to be dependency-light: `numpy`, `pandas`, and `scipy` only. (You can drop SciPy if you prefer, but `scipy.stats` is handy for bootstrap diagnostics.)

Copy into a `.py` or use directly in a Jupyter notebook.

[Code omitted for brevity - see `_ats.py`]

---

## 6. Seasonal ATS: Methodological Improvement (Stratified ATS)

This section describes the **Stratified ATS Estimator** implemented in `MannKenSen`, which differs intentionally from the reference `censeaken` R script.

### The Problem with the `censeaken` Method

The `censeaken` R script calculates the overall seasonal trend slope by running the standard, non-seasonal `cenken` (ATS) function on the **entire dataset at once**. It treats all data points as a single group, effectively ignoring the seasonal structure during slope estimation.
*   **Issue:** In datasets with strong seasonality (e.g., winter values always lower than summer values), comparing points across seasons introduces significant noise and bias. The slope becomes dominated by seasonal differences rather than the long-term trend.

### The Solution: Stratified ATS

To provide a more robust seasonal trend estimate, `MannKenSen` implements a **Stratified Akritas-Theil-Sen Estimator**. This method respects the independence of seasons, similar to how the Seasonal Kendall test respects seasons for p-value calculation.

**Methodology:**

1.  **Stratified Score Function:**
    Instead of minimizing the Kendall score $S(\beta)$ for the whole dataset, we minimize the **sum of seasonal scores**:
    $$ S_{total}(\beta) = \sum_{k=1}^{m} S_k(\beta) $$
    where $S_k(\beta)$ is the ATS score calculated **only using data pairs within season $k$**.
    *   This ensures that we only compare "apples to apples" (e.g., January 2000 vs. January 2001), eliminating the noise from cross-season comparisons.

2.  **Root Finding:**
    We find the single slope $\beta^*$ such that $S_{total}(\beta^*) = 0$. This single slope represents the overall trend magnitude common to all seasons.

3.  **Stratified Bootstrap:**
    Confidence intervals are calculated using a stratified bootstrap. We resample residuals **independently within each season** to preserve the sample size and variance structure of each season.

4.  **Intercept:**
    Once the global slope $\beta^*$ is determined, the intercept is estimated as the median of the residuals (using the Turnbull estimator) across the **entire dataset**. This centers the trend line correctly relative to the overall data distribution.

**Python Recipe (Stratified ATS):**

The `seasonal_trend_test` function automatically handles this when `sens_slope_method='ats'` is selected. Internally, it calls `seasonal_ats_slope`:

```python
# Internal call structure
overall_ats = seasonal_ats_slope(
    x=t_vector,
    y=values,
    censored=censored_flags,
    seasons=season_ids,  # Key addition: grouping by season
    ...
)
```

This approach yields a slope that is consistent with the Seasonal Kendall test's logic and is robust to strong seasonal cycles.

---

## 7. Confidence intervals and uncertainty

* **Analytic variance** for ATS exists (Akritas), but implementing it correctly is fairly involved.

* **Bootstrap** (resample indices, preserving censoring) is a practical, robust way to get CI — we implement this above. Note: naive bootstrap may be optimistic if `n` is small or censoring extreme; use `n_boot >= 500–2000` when possible, but watch runtime. ([pure.psu.edu][1])

* **Diagnostic flags**:

  * `prop_censored >= 0.15` → warn (Helsel rule-of-thumb: <~15% ideal for simple substitution; ATS is better but you will still lose precision). ([cran.r-project.org][5])
  * `pairwise_ties_frac > 0.5` → many ties; slope unreliable.
  * If bootstrap CI includes zero → slope not significant.

---

## 8. Concrete comparison: ATS vs LWP repeated with references

* **Trend test**: LWP uses Helsel-style censored Kendall which matches NADA-style censored Kendall used by `cenken` for trend **direction / p-values**. So trend detection (increasing/decreasing) will be the same between packages in many cases. 

* **Slope estimator**:

  * `cenken`/`ATS` — `β` is the Akritas–Theil–Sen solution by inverting the censored Kendall statistic (interval comparisons); theoretically principled, unbiased under mild assumptions, and consistent for censored data. ([pure.psu.edu][1])
  * **LWP** — substitutes censored values (`LOD*0.5` for left; `LOD*1.1` for right) then computes ordinary Theil–Sen. This is *not* ATS and can be biased if censoring is moderate/large or LODs change over time. LWP documents the heuristic and its limitations and emits warnings when censoring is heavy. 

* **When they differ**: they will often coincide under *light* censoring and when LODs are stable. They diverge when:

  * Many nondetects (ties dominate)
  * Multiple LOD values exist and LOD changes over time
  * Censoring pattern is non-random or related to time → substituted values skew change over time (creates spurious trends).

**Recommendation:** replace LWP slope with ATS for a principled alternative in your Python package; keep LWP Kendall p-values (they are consistent) or compute censored Kendall via the interval logic in ATS code for perfect consistency.

(See LWP docs section “Handling Censored Values” for exact LWP substitution rules and warnings.) 

---

## 9. Practical notes, pitfalls and tests to perform

1. **Edge cases**:

   * If there are `<= 4` non-censored points or `<3` unique uncensored values, you will have little power; LWP and many guidelines will flag “not analysed.” Consider flagging or returning `None`. 
   * If the proportion censored > ~50%, medians may be undefined; ATS can still run but results will be very uncertain.

2. **Performance**:

   * The `S_of_beta` calculation is O(n²). For `n` up to ~1000 this is usually fine in pure Python if optimized; if you expect large `n` consider numba/C or an optimized C/Fortran routine.

3. **Testing**:

   * Test your Python ATS against **R/NADA** on shared examples:

     * Create synthetic datasets with known slope and censoring, compute `cenken` in R, compare to your `ats_slope`.
     * Test seasonal datasets and cross-validate with `censeaken`.
   * R reproducible examples are in NADA/NADA2 documentation; use those to validate.

4. **Bootstrap**:

   * Use `n_boot = 1000` for production; smaller numbers (200–500) for quick checks. Use percentile CI or bias-corrected (BCa) if you want more accuracy.

5. **Reporting**:

   * Always print `prop_censored` and bootstrap `n_samples` used for CI.

---

## 10. Additional enhancements & alternatives

* **Implement Turnbull EM** to estimate intercept exactly and to compute more formal variance (port NADA's Turnbull code / use existing interval-censoring EM implementations). See Turnbull (1976). ([JSTOR][3])

* **Analytic variance**: implement Akritas asymptotic variance if you want non-bootstrap CIs. Requires careful implementation (see Akritas 1995). ([pure.psu.edu][1])

* **Bayesian censored regression** (Tobit / censored-likelihood): for complex models or if you accept distributional assumptions, `pystan`/`cmdstanpy`/`PyMC` can fit censored regression models and give full posteriors. Useful for small sample sizes or hierarchical models but less robust than ATS if distributional assumptions fail. ([cran.r-project.org][5])

* **Multiple imputation using survival fits**: fit a survival / parametric model for `y` (given censoring), draw imputed values below LOD, then run a standard Theil–Sen on each imputed dataset and pool results (Rubin pooling). This captures imputation uncertainty; more work but viable. See Helsel for ROS / imputation ideas. ([cran.r-project.org][5])

---

## 11. Quick-check list before swapping to ATS in your package

1. Ensure **x (time)** is numeric and not censored. If `x` may be censored, ATS needs extension (rare in trend-time).
2. Provide: `y`, `censored` boolean, `cen_type` (`'lt'|'gt'|None`), and `lod` numeric LOD per row.
3. Compute ATS with the provided `ats_slope` wrapper and show diagnostics (`prop_censored`).
4. For seasonal analysis, compute the overall trend line using `ats_slope` on the **entire dataset**, per the guidance in Section 6.
5. Provide bootstrap CI and a flag/warning when censoring is high.
6. Validate against R/NADA on a few real-life examples (I can help write R->CSV test harness if you want).

---

## 12. Minimal example: compare LWP-style substitution vs ATS (pseudo-code)

```python
# assume y_obs, censored, lod, x as before
# LWP substitute:
y_lwp = np.where(censored, 0.5 * lod, y_obs)
# compute ordinary Theil-Sen on (x, y_lwp) e.g. using scipy or pairwise slopes median
# compare to ats_slope(...) from above
```

If the two differ substantially, prefer ATS unless you have a specific operational reason to keep LWP's substitution.

---

## 13. R Script File Organization

The Akritas-Theil-Sen (ATS) method implementation in the `Example_Files/R/NADA2/` directory is structured across several key files:

*   **`NADA_ken.R` (Core Engine)**: This script contains the fundamental statistical logic. The central function is `cenken`, which computes the ATS slope and intercept for a given dataset. It handles the complex calculations involving censored data.

*   **`ATS.R` (High-Level Wrapper)**: This script provides a full-featured, user-friendly interface for non-seasonal ATS analysis. It calls the `cenken` function from `NADA_ken.R` to perform the core calculations and adds features like automatic logging, plotting, and data preparation.

*   **`ATSmini.R` (Simplified Wrapper)**: This is a lightweight, faster wrapper, also for non-seasonal data. It calls `cenken` directly and is primarily intended for internal use by other functions (like `censeaken`) where the overhead of the full `ATS.R` script is unnecessary.

*   **`censeaken.R` (Seasonal ATS)**: This script implements the seasonal version of the ATS test. For each season present in the data, it calls `ATSmini` to calculate trend statistics *for that season*. The **overall trend line** is calculated by calling `ATSmini` on the entire dataset. The **overall p-value** is calculated via a permutation test on the sum of the seasonal statistics.

In summary, the non-seasonal ATS functionality is driven by `NADA_ken.R`, with `ATS.R` and `ATSmini.R` acting as user-facing and internal wrappers, respectively. The seasonal analysis is handled by `censeaken.R`, which leverages the non-seasonal engine for its per-season calculations and its overall trend line calculation.

---

## 14. References and sources

* Akritas, M.G., Murphy,S.A., LaValley, M.P. (1995). *The Theil–Sen estimator with doubly censored data and applications*. Journal of the American Statistical Association. (ATS method). ([pure.psu.edu][1])
* NADA package: `cenken` documentation (Compute censored Kendall’s tau and ATS line). ([rdocumentation.org][4])
* NADA2 package: `censeaken` (seasonal ATS/Kendall) and NADA2 manual. ([rdocumentation.org][6])
* Turnbull, B. (1976). *The Empirical Distribution Function with Arbitrarily Grouped, Censored and Truncated Data* (Turnbull estimator for interval censoring). ([JSTOR][3])
* Helsel, D.R. (2005, 2012). *Nondetects and Data Analysis* / *Statistics for Censored Environmental Data* (guidance on ROS, Kaplan–Meier, substitution cautions). ([cran.r-project.org][5])
* LWP-Trends (v2502) — documentation (explicit description of LWP censor handling: substitution 0.5 and 1.1, Kendall tie rules, warnings). 

---


[1]: https://pure.psu.edu/en/publications/the-theil-sen-estimator-with-doubly-censored-data-and-application/?utm_source=chatgpt.com "The Theil-Sen estimator with doubly censored data and ..."
[2]: https://en.wikipedia.org/wiki/Theil%E2%80%93Sen_estimator?utm_source=chatgpt.com "Theil–Sen estimator"
[3]: https://www.jstor.org/stable/2984980?utm_source=chatgpt.com "The Empirical Distribution Function with Arbitrarily Grouped ..."
[4]: https://www.rdocumentation.org/packages/NADA/versions/1.6-1.2/topics/cenken?utm_source=chatgpt.com "cenken function"
[5]: https://cran.r-project.org/web/packages/NADA/NADA.pdf?utm_source=chatgpt.com "NADA: Nondetects and Data Analysis for Environmental Data"
[6]: https://www.rdocumentation.org/packages/NADA2/versions/2.0.1/topics/censeaken?utm_source=chatgpt.com "censeaken Seasonal Kendall permutation test on censored ..."
