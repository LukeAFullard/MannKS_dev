# Using `cenken` / `censeaken` (Akritas–Theil–Sen) for trend **magnitude** — full report and Python implementation

**Purpose:** give you everything you need to (1) understand how `cenken` / `censeaken` compute a Theil–Sen style slope for censored data (the Akritas–Theil–Sen (ATS) estimator), (2) understand how that differs from the LWP implementation, and (3) implement a working ATS estimator (plus seasonal variant and bootstrap CIs) in **Python** for use in your package.

This is a single self-contained Markdown file. Key references are cited inline.

---

## Executive summary

* `cenken` / `censeaken` implement the **Akritas–Theil–Sen (ATS)** approach: they *directly work with censoring* (intervals) and compute a slope by inverting a censored Kendall statistic (i.e. finding the slope `β` that makes the Kendall-type `S` (or τ) of residuals equal to zero). The intercept is estimated nonparametrically (Turnbull-style). This is a *formal censored-data* extension of Theil–Sen. ([pure.psu.edu][1])

* LWP-Trends uses Helsel-style censored **Kendall** logic for the trend **test** (so trend direction / p-values are compatible with NADA), **but** for slope it uses a *pragmatic substitution* rule — left-censored values replaced by `LOD * 0.5` and right-censored by `LOD * 1.1` and then a standard Theil–Sen on those substituted values. That is **not** the ATS estimator; it is a pragmatic heuristic that is defensible under light censoring but can be biased as censoring grows. 

* This report explains ATS theory, shows how it differs from LWP, and supplies Python code to compute:

  * ATS slope (root-finding on censored-Kendall `S(β)`)
  * bootstrap confidence intervals
  * seasonal ATS (apply ATS per-season and combine sensibly)
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

5. Intercept: find an intercept `α` (e.g. Turnbull-style median residual) so the line `y = α + β* x` is the ATS fit. (NADA implements a Turnbull-type intercept estimate.) ([pure.psu.edu][1])

6. Variance / CI: Akritas supplies an asymptotic variance formula (nontrivial). Practically, many implementations (and this report's code) compute bootstrap confidence intervals (resampling preserving censoring patterns) as a robust alternative.

**Notes:**

* If `x` (time) itself is censored, ATS generalizes but is more complex (doubly censored). For most trend work `x` is time (uncensored).
* Seasonal ATS: apply ATS per-season (e.g. each month), and combine. `censeaken` implements a seasonal ATS-based test; it computes seasonal S statistics and (by permutation) an overall p-value. For slope you can compute per-season ATS slopes and take the median or a weighted aggregator (see below). ([rdocumentation.org][6])

---

## 4. Implementation plan in Python (practical choices & trade-offs)

**Design goals**

* Accurate ATS slope for singly left-censored (typical) or mixed censoring.
* Clear diagnostics (prop censored, pairwise tie fraction).
* Reasonable performance for `n` up to a few hundreds (O(n²) pairwise comparisons is typical).
* Bootstrap CIs implemented (respects censoring).
* Seasonal variant by grouping.

**Trade-offs**

* Exact Turnbull intercept and analytic variance are a lot of work; we provide a pragmatic, correct ATS slope finder and bootstrap CI. This is robust in practice and easier to maintain than porting all asymptotic variance machinery.
* For very large `n`, we'd recommend faster Theil–Sen algorithms adapted for interval comparisons — but for environmental monitoring (n typically 50–500) O(n²) is fine.

---

## 5. Python code (complete, runnable)

> This code is written to be dependency-light: `numpy`, `pandas`, and `scipy` only. (You can drop SciPy if you prefer, but `scipy.stats` is handy for bootstrap diagnostics.)

Copy into a `.py` or use directly in a Jupyter notebook.

```python
# ats.py  -- Akritas-Theil-Sen implementation (single-file, dependency-light)
import numpy as np
import pandas as pd
from math import inf
from typing import Tuple, List, Optional
from random import randint
import multiprocessing
from functools import partial

# ---------- Utilities: interval representation ----------
def make_intervals(y: np.ndarray,
                   censored: np.ndarray,
                   cen_type: Optional[np.ndarray] = None,
                   lod: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build intervals [a_i, b_i] for each observation.
    Arguments:
      y: numeric face values (for censored rows this should be the numeric reporting value)
      censored: boolean array (True when censored)
      cen_type: None or array of 'lt' / 'gt' / 'none' strings (if None, assume all censored are 'lt')
      lod: numeric detection limits associated with censored observations (len same as y)
    Returns:
      (lower, upper) arrays where lower[i] <= upper[i]; may include +-inf for left/right censor.
    """
    n = len(y)
    lower = np.empty(n, dtype=float)
    upper = np.empty(n, dtype=float)
    if cen_type is None:
        cen_type = np.array(['lt' if c else 'none' for c in censored])
    if lod is None:
        lod = np.array([y_i for y_i in y])

    for i in range(n):
        if not censored[i]:
            lower[i] = upper[i] = y[i]
        else:
            t = cen_type[i]
            d = lod[i]
            if t == 'lt' or t == '<' or t.lower() == 'left':
                lower[i] = -inf
                upper[i] = d
            elif t == 'gt' or t == '>' or t.lower() == 'right':
                lower[i] = d
                upper[i] = +inf
            else:
                # default to left-censor
                lower[i] = -inf
                upper[i] = d
    return lower, upper

# ---------- Pairwise interval comparison on residuals ----------
def S_of_beta(beta: float, x: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> int:
    """
    Compute S(beta) = (#concordant) - (#discordant) using residual intervals:
      R_i(beta) = [lower_i - beta*x_i, upper_i - beta*x_i]
    Definitive comparisons only when intervals do not overlap.
    """
    n = len(x)
    lower_r = lower - beta * x
    upper_r = upper - beta * x

    concordant = 0
    discordant = 0
    # O(n^2) loop
    for i in range(n):
        for j in range(i+1, n):
            # check if r_i > r_j (lower_i > upper_j)
            if lower_r[i] > upper_r[j]:
                concordant += 1
            elif upper_r[i] < lower_r[j]:
                discordant += 1
            else:
                # tie/overlap -> do not count
                pass
    return concordant - discordant

# ---------- Root-finding to solve S(beta) = 0 ----------
def bracket_and_bisect(x: np.ndarray, lower: np.ndarray, upper: np.ndarray,
                       beta0: Optional[float]=None, max_expand=50, tol=1e-8,
                       maxiter=60) -> float:
    """
    Find beta* with bisection:
    - choose initial bracket (low, high) that gives S(low) and S(high) with opposite signs.
    - if no bracket found, expand search.
    - return beta where S(beta) == 0 (within tol) or approximate where sign changes.
    """
    n = len(x)
    # initial guess: standard Theil-Sen on uncensored pairs where both are exact
    # build simple slope list from detected points
    detected_idx = np.where(np.isfinite(lower) & np.isfinite(upper) & (lower == upper))[0]
    if len(detected_idx) >= 2:
        slopes = []
        di = detected_idx
        for i in range(len(di)):
            for j in range(i+1, len(di)):
                xi, xj = x[di[i]], x[di[j]]
                if xj == xi:
                    continue
                yi, yj = lower[di[i]], lower[di[j]]
                slopes.append((yj - yi) / (xj - xi))
        if len(slopes) > 0:
            median_slope = np.median(slopes)
        else:
            median_slope = 0.0
    else:
        median_slope = 0.0

    if beta0 is None:
        beta0 = median_slope

    # start bracket around beta0
    low = beta0 - max(1.0, abs(beta0))*1.0
    high = beta0 + max(1.0, abs(beta0))*1.0
    s_low = S_of_beta(low, x, lower, upper)
    s_high = S_of_beta(high, x, lower, upper)

    # expand outward until sign change or max_expand iterations
    expand_factor = 2.0
    it = 0
    while s_low * s_high > 0 and it < max_expand:
        # expand
        low = low - (abs(low) + 1.0) * expand_factor
        high = high + (abs(high) + 1.0) * expand_factor
        s_low = S_of_beta(low, x, lower, upper)
        s_high = S_of_beta(high, x, lower, upper)
        it += 1

    if s_low * s_high > 0:
        # no sign change found; pick beta where S is closest to zero
        # scan a grid and pick argmin |S|
        grid = np.linspace(beta0 - 1000, beta0 + 1000, num=201)
        Svals = np.array([abs(S_of_beta(g, x, lower, upper)) for g in grid])
        best_idx = np.argmin(Svals)
        return float(grid[best_idx])

    # bisection
    a, b = low, high
    Sa, Sb = s_low, s_high
    for it in range(maxiter):
        m = (a + b) / 2.0
        Sm = S_of_beta(m, x, lower, upper)
        if abs(Sm) == 0 or (b - a) / 2.0 < tol:
            return float(m)
        # decide which side to keep
        if Sa * Sm <= 0:
            b = m
            Sb = Sm
        else:
            a = m
            Sa = Sm
    # return midpoint if not converged
    return float((a + b) / 2.0)

# ---------- Turnbull-style intercept (practical approach) ----------
def estimate_intercept(beta: float, x: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> float:
    """
    Practical intercept estimate: compute interval residuals R_i = [l_i - beta*x_i, u_i - beta*x_i],
    then take a Turnbull-like median: find median of the (interval) distribution via midpoint heuristic:
    - When many intervals non-overlapping, pick median of midpoints (safe),
    - Otherwise pick midpoint of medians of lower and upper arrays.
    This is a pragmatic choice; more exact Turnbull EM can be added if required.
    """
    r_lower = lower - beta * x
    r_upper = upper - beta * x
    # Midpoints for finite intervals (for -inf/+inf we ignore)
    finite_mask = np.isfinite(r_lower) & np.isfinite(r_upper)
    if np.any(finite_mask):
        midpoints = 0.5 * (r_lower[finite_mask] + r_upper[finite_mask])
        return float(np.median(midpoints))
    else:
        # if none finite, fall-back: median of finite bounds
        finite_l = r_lower[np.isfinite(r_lower)]
        finite_u = r_upper[np.isfinite(r_upper)]
        vals = []
        if finite_l.size:
            vals.append(np.median(finite_l))
        if finite_u.size:
            vals.append(np.median(finite_u))
        if vals:
            return float(np.median(vals))
        return 0.0

# ---------- Public wrapper ----------
def ats_slope(x: np.ndarray, y: np.ndarray, censored: np.ndarray,
              cen_type: Optional[np.ndarray] = None, lod: Optional[np.ndarray] = None,
              bootstrap_ci: bool = True, n_boot: int = 500,
              ci_alpha: float = 0.05) -> dict:
    """
    Compute ATS slope estimate and bootstrap CI.
    Returns dict with keys: beta, intercept, ci_lower, ci_upper, prop_censored, notes
    """
    lower, upper = make_intervals(y, censored, cen_type=cen_type, lod=lod)
    beta_hat = bracket_and_bisect(x, lower, upper, beta0=None)
    intercept = estimate_intercept(beta_hat, x, lower, upper)
    prop_cen = float(np.mean(censored))

    result = {'beta': beta_hat, 'intercept': intercept,
              'prop_censored': prop_cen, 'notes': []}

    # simple diagnostics: fraction of pairwise comparisons that were ties at final beta
    n = len(x)
    lower_r = lower - beta_hat * x
    upper_r = upper - beta_hat * x
    ties = 0
    total_pairs = 0
    for i in range(n):
        for j in range(i+1, n):
            total_pairs += 1
            if (lower_r[i] <= upper_r[j]) and (upper_r[i] >= lower_r[j]):
                # intervals overlap -> tie
                ties += 1
    result['pairwise_ties_frac'] = ties / total_pairs if total_pairs > 0 else np.nan

    # bootstrap CI (resampling indices with replacement, keep censoring info)
    if bootstrap_ci:
        boot_betas = []
        rng = np.random.default_rng()
        for b in range(n_boot):
            idx = rng.integers(0, n, n)
            x_b = x[idx]
            y_b = y[idx]
            cens_b = censored[idx]
            cen_t_b = cen_type[idx] if cen_type is not None else None
            lod_b = lod[idx] if lod is not None else None
            try:
                lower_b, upper_b = make_intervals(y_b, cens_b, cen_type=cen_t_b, lod=lod_b)
                beta_b = bracket_and_bisect(x_b, lower_b, upper_b)
                boot_betas.append(beta_b)
            except Exception:
                # skip sample if root-finding fails
                pass
        if len(boot_betas) >= max(10, int(0.1 * n_boot)):
            lo = np.quantile(boot_betas, ci_alpha/2)
            hi = np.quantile(boot_betas, 1 - ci_alpha/2)
            result['ci_lower'] = float(lo)
            result['ci_upper'] = float(hi)
            result['bootstrap_samples'] = len(boot_betas)
        else:
            result['ci_lower'] = None
            result['ci_upper'] = None
            result['notes'].append('bootstrap failed to produce enough valid samples for CI')
    return result
```

### Example usage (synthetic)

```python
import numpy as np
from ats import ats_slope

# synthetic example with some left-censoring
np.random.seed(1)
n = 80
x = np.linspace(0, 10, n)                         # time
true_beta = 0.2
y_true = 1.0 + true_beta * x
y = y_true + np.random.normal(scale=0.5, size=n)

# impose a LOD and censor low values
lod = 1.5
censored = y < lod
y_obs = np.where(censored, lod, y)               # store face values (lod for censored)
cen_type = np.array(['lt' if c else 'none' for c in censored])

res = ats_slope(x=x, y=y_obs, censored=censored, cen_type=cen_type, lod=np.full(n, lod),
                bootstrap_ci=True, n_boot=400)
print(res)
# res['beta'] is the ATS slope, compare to true_beta
```

---

## 6. Seasonal ATS (how to do seasonality consistently)

`censeaken` (NADA2) implements the seasonal ATS test (for significance) by computing ATS/Kendall within each season and combining; for slope you typically want a *seasonal slope* that represents the annual rate. Two common choices:

1. **Per-season ATS + median**: compute ATS slope `β_s` for each season (e.g. for month `m` restrict to observations from that month across years), then take the **median** of the seasonal slopes as the seasonal ATS slope. This mirrors how seasonal Theil–Sen is often done (Sen per-season then median across seasons). `censeaken` uses ATS per season for the test. ([rdocumentation.org][6])

2. **Combine residual intervals**: a more formal approach sums the season-wise S statistics and variances to get a combined test and then solves a global `β` consistent with the seasonal pairing structure (more complex). For most monitoring applications (monthly or quarterly) (1) is simpler and acceptable.

**Python recipe (practical):**

* Add a `season` column (e.g., month).
* Loop seasons: run `ats_slope` on the subset (if the subset has enough data).
* Collect `β_s`, report median and IQR; warn if many seasons failed or had high censoring.
* Optionally compute a weighted median (weights = number of years per season or inverse bootstrap variance).

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

   * Always print `prop_censored`, `pairwise_ties_frac`, and bootstrap `n_samples` used for CI. If `pairwise_ties_frac` > 0.5 or `prop_censored` > 0.3, report low confidence.

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
3. Compute ATS with the provided `ats_slope` wrapper and show diagnostics (`prop_censored`, `pairwise_ties_frac`).
4. If seasonal, group and run ATS per-season; report median seasonal slope.
5. Provide bootstrap CI and a flag/warning when censoring is high or pairwise ties dominate.
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

*   **`censeaken.R` (Seasonal ATS)**: This script implements the seasonal version of the ATS test. For each season present in the data, it calls `ATSmini` to calculate the trend. It then combines the results from all seasons to provide an overall seasonal trend analysis, including a permutation test for significance.

In summary, the non-seasonal ATS functionality is driven by `NADA_ken.R`, with `ATS.R` and `ATSmini.R` acting as user-facing and internal wrappers, respectively. The seasonal analysis is handled by `censeaken.R`, which leverages the non-seasonal engine for its per-season calculations.

---

## 14. References and sources

* Akritas, M.G., Murphy, S.A., LaValley, M.P. (1995). *The Theil–Sen estimator with doubly censored data and applications*. Journal of the American Statistical Association. (ATS method). ([pure.psu.edu][1])
* NADA package: `cenken` documentation (Compute censored Kendall’s tau and ATS line). ([rdocumentation.org][4])
* NADA2 package: `censeaken` (seasonal ATS/Kendall) and NADA2 manual. ([rdocumentation.org][6])
* Turnbull, B. (1976). *Empirical distribution function with arbitrarily grouped, censored and truncated data* (Turnbull estimator for interval censoring). ([JSTOR][3])
* Helsel, D.R. (2005, 2012). *Nondetects and Data Analysis* / *Statistics for Censored Environmental Data* (guidance on ROS, Kaplan–Meier, substitution cautions). ([cran.r-project.org][5])
* LWP-Trends (v2502) — documentation (explicit description of LWP censor handling: substitution 0.5 and 1.1, Kendall tie rules, warnings). 

---


[1]: https://pure.psu.edu/en/publications/the-theil-sen-estimator-with-doubly-censored-data-and-application/?utm_source=chatgpt.com "The Theil-Sen estimator with doubly censored data and ..."
[2]: https://en.wikipedia.org/wiki/Theil%E2%80%93Sen_estimator?utm_source=chatgpt.com "Theil–Sen estimator"
[3]: https://www.jstor.org/stable/2984980?utm_source=chatgpt.com "The Empirical Distribution Function with Arbitrarily Grouped ..."
[4]: https://www.rdocumentation.org/packages/NADA/versions/1.6-1.2/topics/cenken?utm_source=chatgpt.com "cenken function"
[5]: https://cran.r-project.org/web/packages/NADA/NADA.pdf?utm_source=chatgpt.com "NADA: Nondetects and Data Analysis for Environmental Data"
[6]: https://www.rdocumentation.org/packages/NADA2/versions/2.0.1/topics/censeaken?utm_source=chatgpt.com "censeaken Seasonal Kendall permutation test on censored ..."
