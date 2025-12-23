# ats.py  -- Akritas-Theil-Sen implementation (single-file, dependency-light)
import numpy as np
import pandas as pd
from math import inf
from typing import Tuple, List, Optional
from random import randint

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
