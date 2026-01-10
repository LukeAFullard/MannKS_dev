import numpy as np
from scipy.optimize import differential_evolution, minimize
from scipy.stats import norm
import warnings
from ._stats import (
    _sens_estimator_unequal_spacing,
    _sens_estimator_censored,
    _mk_score_and_var_censored,
    _confidence_intervals
)

def _fast_huber_fit(X, y, epsilon=1.35, max_iter=10, tol=1e-5):
    """
    Custom Iteratively Reweighted Least Squares (IRLS) solver for Huber Regression.
    Optimized for speed using pure NumPy vectorization.

    Solves: beta = argmin sum(L_delta(y_i - x_i.T * beta))
    """
    n, p = X.shape

    # 1. Initialize with OLS
    # Add small ridge for stability in case of rank deficiency
    XtX = X.T @ X
    XtY = X.T @ y
    ridge = np.eye(p) * 1e-8

    try:
        beta = np.linalg.solve(XtX + ridge, XtY)
    except np.linalg.LinAlgError:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]

    for _ in range(max_iter):
        y_pred = X @ beta
        residuals = y - y_pred

        # Robust scale estimate (MAD)
        # MAD = median(|r - median(r)|)
        resid_median = np.median(residuals)
        mad = np.median(np.abs(residuals - resid_median))
        sigma = mad / 0.6744897501960817

        if sigma < 1e-10:
            # Perfect fit or zero variance
            break

        # Calculate Weights
        # w_i = 1             if |r_i| <= epsilon * sigma
        # w_i = epsilon*sigma / |r_i|  if |r_i| > epsilon * sigma

        # Standardize residuals
        standard_resids = (residuals) / sigma
        abs_r = np.abs(standard_resids)

        weights = np.ones(n)
        mask = abs_r > epsilon
        weights[mask] = epsilon / abs_r[mask]

        # Weighted Least Squares Step
        # beta = (X.T W X)^-1 X.T W y
        # Can be computed as (X * sqrt(w)).T (X * sqrt(w)) ...

        # Vectorized weighted matrices
        # W is diagonal, so X.T W X = X.T @ (weights[:, None] * X)
        XtWX = X.T @ (X * weights[:, None])
        XtWy = X.T @ (y * weights)

        try:
            beta_new = np.linalg.solve(XtWX + ridge, XtWy)
        except np.linalg.LinAlgError:
            # Fallback to slower but robust lstsq
            beta_new = np.linalg.lstsq(X * np.sqrt(weights[:, None]), y * np.sqrt(weights), rcond=None)[0]

        if np.allclose(beta, beta_new, atol=tol):
            beta = beta_new
            break

        beta = beta_new

    return beta

def _huber_loss(residuals, epsilon=1.35, sigma=1.0):
    """
    Calculates the Huber loss for a vector of residuals.
    L = 0.5 * r^2               if |r| <= epsilon
    L = epsilon * (|r| - 0.5*epsilon) if |r| > epsilon
    """
    abs_r = np.abs(residuals)

    # If sigma is provided, scale residuals?
    # Usually Huber loss is defined on raw residuals with a scale parameter
    # or residuals are pre-scaled.
    # To match _fast_huber_fit logic, let's assume residuals are raw and we just sum the loss.
    # But for optimization metric, we often fix sigma=1 or estimate it.
    # Here we define the standard Huber function.

    mask = abs_r <= epsilon
    loss = np.zeros_like(residuals)

    loss[mask] = 0.5 * residuals[mask]**2
    loss[~mask] = epsilon * (abs_r[~mask] - 0.5 * epsilon)

    return np.sum(loss)


class RobustSegmentedTrend:
    """
    Scout and Refine: Robust Segmented Regression.

    Phase 1 (The Scout): Uses Fast Huber Regression (IRLS) and Differential Evolution
    to robustly detect breakpoint locations.

    Phase 2 (The Refiner): Uses Mann-Kendall / Sen's Slope on the identified
    segments to estimate final parameters (slopes, intercepts, CIs).
    """

    def __init__(self, n_breakpoints=1, epsilon=1.35, fit_intercept=True, optimizer_kwargs=None, refine=True):
        self.n_breakpoints = n_breakpoints
        self.epsilon = epsilon
        self.fit_intercept = fit_intercept
        self.optimizer_kwargs = optimizer_kwargs or {}
        self.refine = refine

        self.breakpoints_ = None
        self.segments_ = None
        self.model_loss_ = None # AIC/BIC proxy can be stored here

    def fit(self, t, x, censored=None, cen_type=None, lt_mult=0.5, gt_mult=1.1, initial_guess=None):
        """
        Fit the robust segmented model.

        Args:
            t (array-like): Time/Independent variable.
            x (array-like): Value/Dependent variable.
            censored (array-like, optional): Boolean array indicating censored data.
            cen_type (array-like, optional): String array ('lt', 'gt') for censoring type.
            lt_mult (float): Multiplier for left-censored substitution (Refiner phase).
            gt_mult (float): Multiplier for right-censored substitution (Refiner phase).
            initial_guess (array-like, optional): Hint for breakpoint locations (e.g. from simpler model).
        """
        t = np.asarray(t)
        x = np.asarray(x)

        # Sort data by time
        sort_idx = np.argsort(t)
        t = t[sort_idx]
        x = x[sort_idx]

        if censored is not None:
            censored = np.asarray(censored)[sort_idx]
            cen_type = np.asarray(cen_type)[sort_idx]

            # For SCOUT phase (Huber), we need numeric values.
            # Perform substitution.
            x_scout = x.copy().astype(float)
            x_scout[cen_type == 'lt'] *= lt_mult
            x_scout[cen_type == 'gt'] *= gt_mult
        else:
            x_scout = x

        self.n_samples_ = len(x)
        t_min, t_max = t[0], t[-1]

        # --- PHASE 1: THE SCOUT (Detection) ---

        if self.n_breakpoints > 0:
            bounds = [(t_min, t_max)] * self.n_breakpoints

            # Objective function for DE
            def objective(breakpoints):
                # Sort breakpoints to ensure validity
                bps = np.sort(breakpoints)

                # Check for validity (must be within range and distinct)
                # We can enforce a small buffer
                if bps[0] <= t_min or bps[-1] >= t_max:
                    return 1e9 # Penalty
                if self.n_breakpoints > 1 and np.any(np.diff(bps) < (t_max - t_min) * 0.01):
                    return 1e9 # Penalty for too close breakpoints

                # Construct Design Matrix for Continuous Piecewise Linear
                # Basis: 1, t, (t - b1)+, (t - b2)+ ...

                X_mat = np.zeros((len(t), 2 + self.n_breakpoints))
                X_mat[:, 0] = 1.0 # Intercept
                X_mat[:, 1] = t

                for i, bp in enumerate(bps):
                    basis = t - bp
                    basis[basis < 0] = 0
                    X_mat[:, 2 + i] = basis

                # Fit Huber
                beta = _fast_huber_fit(X_mat, x_scout, epsilon=self.epsilon)

                # Calculate Loss
                y_pred = X_mat @ beta
                resids = x_scout - y_pred

                # We minimize sum of Huber loss
                # Note: fast_huber_fit estimates scale, but for objective function
                # we ideally want a consistent scale.

                # Robust Scale (MAD)
                resid_median = np.median(resids)
                mad = np.median(np.abs(resids - resid_median))
                sigma = mad / 0.6744897501960817

                if sigma < 1e-10:
                    # Perfect fit
                    return -np.inf

                # Scaled Huber Loss
                # To properly compare models with different scales, we must include the
                # scale term in the likelihood: N * log(sigma) + sum(rho(r/sigma))

                rho_sum = _huber_loss((resids - resid_median) / sigma, epsilon=self.epsilon)

                cost = len(resids) * np.log(sigma) + rho_sum

                return cost

            # Run Differential Evolution
            # Merge default settings with user provided kwargs
            de_kwargs = {
                'strategy': 'best1bin',
                'maxiter': 100,
                'popsize': 15,
                'tol': 0.01,
                'mutation': (0.5, 1),
                'recombination': 0.7,
                'polish': True
            }

            # Greedy Initialization / Warm Start
            if initial_guess is not None and len(initial_guess) > 0 and len(initial_guess) < self.n_breakpoints:
                # If we have a guess for K-1 breakpoints, initialize population with it
                # We need popsize * dim individuals.
                # Construct candidates by taking initial_guess and adding 1 random BP

                # Determine population size
                popsize = de_kwargs['popsize']
                if 'popsize' in self.optimizer_kwargs:
                    popsize = self.optimizer_kwargs['popsize']

                n_pop = int(popsize * self.n_breakpoints) # Scipy uses popsize as multiplier

                init_pop = np.random.uniform(t_min, t_max, (n_pop, self.n_breakpoints))

                # Seed the first few individuals with the guess + random BP
                guess = np.asarray(initial_guess)
                # Sort guess to match bounds logic mostly, but DE handles it

                # How many to seed? Let's seed 30% of population
                n_seed = max(1, int(n_pop * 0.3))

                for k in range(n_seed):
                    # Fill first slots with guess
                    init_pop[k, :len(guess)] = guess
                    # Remaining slots random (already set)
                    # Ideally we perturb guess slightly too?
                    # Let's just trust DE mutation.

                # Pass init to kwargs
                de_kwargs['init'] = init_pop

            de_kwargs.update(self.optimizer_kwargs)

            result = differential_evolution(
                objective,
                bounds,
                **de_kwargs
            )

            self.breakpoints_ = np.sort(result.x)

            # --- Optional Polishing (Refinement) ---
            if self.refine and self.n_breakpoints > 0:
                self.breakpoints_ = self._polish_breakpoints(t, x_scout, self.breakpoints_)

        else:
            self.breakpoints_ = np.array([])

        # --- PHASE 2: THE REFINER (Estimation) ---

        # Define segments
        boundaries = np.concatenate(([t_min], self.breakpoints_, [t_max]))
        # Ensure boundaries are unique (if breakpoints coincided with min/max)
        boundaries = np.unique(boundaries)

        self.segments_ = []

        # Loop through segments defined by boundaries
        # Boundaries: [t0, t1, t2, ..., tn]
        # Segments: [t0, t1], [t1, t2], ...

        for i in range(len(boundaries) - 1):
            t_start = boundaries[i]
            t_end = boundaries[i+1]

            # Select data for this segment
            # Use inclusive for start, exclusive for end (except last)
            if i == len(boundaries) - 2:
                mask = (t >= t_start) & (t <= t_end)
            else:
                mask = (t >= t_start) & (t < t_end)

            # Ensure sufficient data
            if np.sum(mask) < 2:
                self.segments_.append({
                    'slope': np.nan, 'intercept': np.nan,
                    'lower_ci': np.nan, 'upper_ci': np.nan,
                    'n': 0
                })
                continue

            t_seg = t[mask]
            x_seg = x[mask]

            if censored is not None:
                cen_seg = censored[mask]
                cen_type_seg = cen_type[mask]

                # Use censored estimator
                slopes = _sens_estimator_censored(
                    x_seg, t_seg, cen_type_seg,
                    lt_mult=lt_mult, gt_mult=gt_mult
                )

                # Mann-Kendall Stats for CI
                # Note: mk_score needs x, t, censored, cen_type
                s, var_s, _, _ = _mk_score_and_var_censored(
                    x_seg, t_seg, cen_seg, cen_type_seg
                )

            else:
                # Use standard estimator
                slopes = _sens_estimator_unequal_spacing(x_seg, t_seg)

                # Dummy censored arrays for MK test
                dummy_cen = np.zeros(len(x_seg), dtype=bool)
                dummy_type = np.full(len(x_seg), 'not', dtype=object)
                s, var_s, _, _ = _mk_score_and_var_censored(
                    x_seg, t_seg, dummy_cen, dummy_type
                )

            # 1. Slope
            slope = np.nanmedian(slopes)

            # 2. Confidence Intervals
            lower_ci, upper_ci = _confidence_intervals(slopes, var_s, alpha=0.05) # Default 95%?

            # 3. Intercept
            # "Calculated robustly as median(y - slope * t)"
            # Only use uncensored data for intercept
            if censored is not None:
                uncensored_mask = ~cen_seg.astype(bool)
                if np.any(uncensored_mask):
                    intercept = np.median(x_seg[uncensored_mask] - slope * t_seg[uncensored_mask])
                else:
                    intercept = np.nan # All censored
            else:
                intercept = np.median(x_seg - slope * t_seg)

            self.segments_.append({
                'slope': slope,
                'intercept': intercept,
                'lower_ci': lower_ci,
                'upper_ci': upper_ci,
                'n': len(x_seg)
            })

    def _polish_breakpoints(self, t, x, initial_bps):
        """
        Refines breakpoint locations by minimizing the Median Absolute Deviation (MAD)
        of the residuals from robust Sen's slope lines.
        """
        # Define local bounds (e.g., +/- 10% of total range around each BP)
        t_range = t.max() - t.min()
        delta = t_range * 0.1
        bounds = [(max(t.min(), bp - delta), min(t.max(), bp + delta)) for bp in initial_bps]

        def objective(bps):
            bps = np.sort(bps)
            # Penalize invalid ordering
            if len(bps) > 1 and np.any(np.diff(bps) < t_range * 0.01):
                return 1e9
            if bps[0] <= t.min() or bps[-1] >= t.max():
                return 1e9

            # Calculate residuals for this configuration using Sen's slope logic
            boundaries = np.concatenate(([t.min()], bps, [t.max()]))
            residuals = []

            for i in range(len(boundaries) - 1):
                t_start = boundaries[i]
                t_end = boundaries[i+1]

                if i == len(boundaries) - 2:
                    mask = (t >= t_start) & (t <= t_end)
                else:
                    mask = (t >= t_start) & (t < t_end)

                t_seg = t[mask]
                x_seg = x[mask]

                if len(x_seg) < 2:
                    continue

                # Calculate Sen's Slope (using fast unequal estimator)
                # Note: We rely on the _stats module logic
                slope = np.nanmedian(_sens_estimator_unequal_spacing(x_seg, t_seg))
                intercept = np.median(x_seg - slope * t_seg)

                y_pred = slope * t_seg + intercept
                residuals.extend(np.abs(x_seg - y_pred))

            if not residuals:
                return 1e9

            # Metric: Median Absolute Deviation (Robust)
            return np.median(residuals)

        # Use Nelder-Mead for local refinement
        res = minimize(
            objective,
            initial_bps,
            bounds=bounds if len(initial_bps) == 1 else None, # minimize supports bounds for L-BFGS-B but not NM usually, let's use Powell or check
            method='L-BFGS-B' if len(initial_bps) == 1 else 'Nelder-Mead' # Nelder-Mead doesn't strict bounds easily, Powell does
        )

        # If optimization failed or didn't improve, return original
        # Actually minimize usually returns result.x regardless
        return np.sort(res.x)

    def predict(self, t):
        """
        Predict values using the fitted segmented model.
        """
        t = np.asarray(t)
        y_pred = np.zeros_like(t, dtype=float)
        y_pred[:] = np.nan

        if self.breakpoints_ is None or len(self.breakpoints_) == 0:
            if self.segments_:
                seg = self.segments_[0]
                return seg['slope'] * t + seg['intercept']
            return y_pred

        bps = np.sort(self.breakpoints_)
        # Use first and last segments for extrapolation

        # First segment
        mask = t < bps[0]
        seg = self.segments_[0]
        y_pred[mask] = seg['slope'] * t[mask] + seg['intercept']

        # Middle segments
        for i in range(len(bps) - 1):
            mask = (t >= bps[i]) & (t < bps[i+1])
            seg = self.segments_[i+1]
            y_pred[mask] = seg['slope'] * t[mask] + seg['intercept']

        # Last segment
        mask = t >= bps[-1]
        seg = self.segments_[-1]
        y_pred[mask] = seg['slope'] * t[mask] + seg['intercept']

        return y_pred
