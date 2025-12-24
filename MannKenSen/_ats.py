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
    Find beta* with bisection. This is a numerically robust implementation that:
    - Uses a data-driven initial bracket based on uncensored data.
    - Scales bracket expansion proportionally to avoid runaway values.
    - Uses a fallback grid search scaled to the final bracket size.
    """
    # Calculate slopes from all uncensored pairs to define the initial search space
    detected_idx = np.where(np.isfinite(lower) & np.isfinite(upper) & (lower == upper))[0]
    slopes = []
    if len(detected_idx) >= 2:
        for i in range(len(detected_idx)):
            for j in range(i + 1, len(detected_idx)):
                xi, xj = x[detected_idx[i]], x[detected_idx[j]]
                if not np.isclose(xj, xi):
                    yi, yj = lower[detected_idx[i]], lower[detected_idx[j]]
                    slopes.append((yj - yi) / (xj - xi))

    # Define the initial search bracket. Using percentiles is robust to
    # extreme outliers that can be generated during bootstrap resampling.
    if slopes:
        low = np.percentile(slopes, 5)
        high = np.percentile(slopes, 95)
        if np.isclose(low, high):
            # If slopes are very similar, create a reasonable bracket around them
            bracket_width = max(1.0, abs(low) * 0.5)
            low -= bracket_width
            high += bracket_width
    else:
        # Fallback if no uncensored slopes are available.
        # This is a critical edge case for bootstrap resampling. The default
        # must be small to avoid numerical instability with datetime slopes.
        low, high = -1e-5, 1e-5

    s_low = S_of_beta(low, x, lower, upper)
    s_high = S_of_beta(high, x, lower, upper)

    # Expand the bracket until the signs of S(low) and S(high) differ
    expand_factor = 1.6
    it = 0
    while s_low * s_high > 0 and it < max_expand:
        width = high - low
        # Expand proportionally to the current bracket width
        low -= width * expand_factor
        high += width * expand_factor
        s_low = S_of_beta(low, x, lower, upper)
        s_high = S_of_beta(high, x, lower, upper)
        it += 1

    # If no sign change was found, perform a grid search over the final bracket
    if s_low * s_high > 0:
        grid = np.linspace(low, high, num=201)
        s_vals = np.array([abs(S_of_beta(g, x, lower, upper)) for g in grid])
        best_idx = np.argmin(s_vals)
        return float(grid[best_idx])

    # Perform bisection search to find the root
    a, b = low, high
    sa, sb = s_low, s_high
    for _ in range(maxiter):
        m = (a + b) / 2.0
        sm = S_of_beta(m, x, lower, upper)
        if sm == 0 or (b - a) / 2.0 < tol:
            return float(m)

        if sa * sm <= 0:
            b, sb = m, sm
        else:
            a, sa = m, sm

    return float((a + b) / 2.0)

# ---------- Turnbull-style intercept (practical approach) ----------
def estimate_intercept_turnbull(residual_lower: np.ndarray, residual_upper: np.ndarray, tol=1e-6, max_iter=100) -> float:
    """
    Estimates the median of interval-censored data using a Turnbull-style approach.
    This is a pragmatic implementation of the core logic, not a full port of a library like Icens.
    It finds the ECDF and returns the 0.5 quantile (median).
    """
    # Get all unique, finite interval endpoints
    endpoints = np.unique(np.concatenate([residual_lower[np.isfinite(residual_lower)],
                                          residual_upper[np.isfinite(residual_upper)]]))

    if len(endpoints) == 0:
        return 0.0
    if len(endpoints) == 1:
        return endpoints[0]

    # The Turnbull sets (intervals between endpoints)
    turnbull_intervals = np.array([(endpoints[i], endpoints[i+1]) for i in range(len(endpoints)-1)])
    midpoints = np.mean(turnbull_intervals, axis=1)

    n_obs = len(residual_lower)
    n_intervals = len(turnbull_intervals)

    # Initialize probabilities for each interval
    p = np.full(n_intervals, 1.0 / n_intervals)

    for _ in range(max_iter):
        p_old = p.copy()

        # E-step: Calculate expected number of observations in each interval
        alpha = np.zeros((n_obs, n_intervals))
        for i in range(n_obs):
            # Find which turnbull intervals are contained within the i-th observation's residual interval
            contained_mask = (turnbull_intervals[:, 0] >= residual_lower[i]) & (turnbull_intervals[:, 1] <= residual_upper[i])

            sum_p_contained = np.sum(p[contained_mask])
            if sum_p_contained > 0:
                alpha[i, contained_mask] = p[contained_mask] / sum_p_contained

        # M-step: Update probabilities
        p = np.sum(alpha, axis=0) / n_obs

        # Check for convergence
        if np.sum(np.abs(p - p_old)) < tol:
            break

    # Calculate ECDF and find the median
    ecdf = np.cumsum(p)

    # Find the first midpoint where the ECDF crosses 0.5
    median_idx = np.where(ecdf >= 0.5)[0]
    if len(median_idx) == 0:
        # If all probabilities are tiny, return the last midpoint
        return midpoints[-1]

    return midpoints[median_idx[0]]


# ---------- Public wrapper ----------
def ats_slope(x: np.ndarray, y: np.ndarray, censored: np.ndarray,
              cen_type: Optional[np.ndarray] = None, lod: Optional[np.ndarray] = None,
              bootstrap_ci: bool = True, n_boot: int = 500,
              ci_alpha: float = 0.05) -> dict:
    """
    Compute ATS slope estimate and bootstrap CI.
    Returns dict with keys: beta, intercept, ci_lower, ci_upper, prop_censored, notes
    """
    # Normalize the time vector to prevent floating point precision issues with large timestamps
    x_min = np.min(x)
    x_norm = x - x_min

    lower, upper = make_intervals(y, censored, cen_type=cen_type, lod=lod)
    beta_hat = bracket_and_bisect(x_norm, lower, upper, beta0=None)

    # Calculate residuals and estimate intercept using Turnbull method
    r_lower = lower - beta_hat * x_norm
    r_upper = upper - beta_hat * x_norm
    intercept_norm = estimate_intercept_turnbull(r_lower, r_upper)

    # De-normalize the intercept to correspond to the original time vector
    intercept = intercept_norm - beta_hat * x_min

    prop_cen = float(np.mean(censored))

    result = {'beta': beta_hat, 'intercept': intercept,
              'prop_censored': prop_cen, 'notes': []}

    # simple diagnostics: fraction of pairwise comparisons that were ties at final beta
    n = len(x)
    lower_r = lower - beta_hat * x_norm
    upper_r = upper - beta_hat * x_norm
    ties = 0
    total_pairs = 0
    for i in range(n):
        for j in range(i+1, n):
            total_pairs += 1
            if (lower_r[i] <= upper_r[j]) and (upper_r[i] >= lower_r[j]):
                # intervals overlap -> tie
                ties += 1
    result['pairwise_ties_frac'] = ties / total_pairs if total_pairs > 0 else np.nan

    # Bootstrap CI using residual resampling to avoid issues with duplicate timestamps
    if bootstrap_ci and n >= 10:
        boot_betas = []
        rng = np.random.default_rng()

        # Calculate fitted values and residual intervals from the original fit
        fitted = intercept_norm + beta_hat * x_norm
        resid_lower = lower - fitted
        resid_upper = upper - fitted

        for b in range(n_boot):
            try:
                # Resample residual indices
                resid_idx = rng.integers(0, n, n)

                # Create a bootstrap sample by adding resampled residuals to fitted values
                y_boot_lower = fitted + resid_lower[resid_idx]
                y_boot_upper = fitted + resid_upper[resid_idx]

                # Refit the model on the bootstrap sample
                # Note: We use the original, un-resampled (but normalized) time vector
                beta_b = bracket_and_bisect(x_norm, y_boot_lower, y_boot_upper)

                # Filter out extreme outliers that can still occur in rare cases
                if np.isfinite(beta_b) and abs(beta_b) < (abs(beta_hat) + 1) * 100:
                     boot_betas.append(beta_b)
            except Exception:
                # Skip sample if root-finding fails
                pass

        if len(boot_betas) >= max(20, int(0.1 * n_boot)):
            lo = np.quantile(boot_betas, ci_alpha/2)
            hi = np.quantile(boot_betas, 1 - ci_alpha/2)
            result['ci_lower'] = float(lo)
            result['ci_upper'] = float(hi)
            result['bootstrap_samples'] = len(boot_betas)
        else:
            result['ci_lower'] = None
            result['ci_upper'] = None
            result['notes'].append(
                f'bootstrap produced only {len(boot_betas)} valid samples '
                f'(need >= {max(20, int(0.1 * n_boot))})'
            )
    return result
