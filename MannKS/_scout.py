import numpy as np
from sklearn.linear_model import HuberRegressor, LinearRegression
from scipy.optimize import differential_evolution
from scipy.stats import theilslopes

def _huber_cost_objective(breakpoints, X, y, min_size=5):
    """
    Calculates the total robust cost of a specific breakpoint configuration.

    Args:
        breakpoints (array): Continuous floats from the optimizer.
        X, y (array): Data.
        min_size (int): Minimum points allowed in a segment.

    Returns:
        float: Total Sum of Absolute Residuals (L1 Cost).
    """
    # 1. Discretize: Convert float candidates to sorted integer indices
    # Map float in [margin, n-margin] directly to integer index
    bkps = np.unique(breakpoints.astype(int))
    bkps = np.sort(bkps)

    # 2. Constraints: Check for segment collapse or edge proximity
    # We add 0 and N to check all segment lengths
    full_bkps = np.concatenate(([0], bkps, [len(y)]))
    segment_lengths = np.diff(full_bkps)

    if np.any(segment_lengths < min_size):
        return np.inf # Invalid solution penalty

    total_cost = 0.0

    # 3. Fast Evaluation Loop
    # We use epsilon=1.35 (95% efficiency) to balance speed/robustness
    huber = HuberRegressor(epsilon=1.35)

    for i in range(len(full_bkps) - 1):
        start, end = full_bkps[i], full_bkps[i+1]

        # Reshape X for sklearn API
        X_sub = X[start:end].reshape(-1, 1)
        y_sub = y[start:end]

        # Basic check for minimum samples for regression
        if len(y_sub) < 2:
             return np.inf

        try:
            huber.fit(X_sub, y_sub)
            y_pred = huber.predict(X_sub)

            # CRITICAL: We sum Absolute Errors (L1), not Squared Errors.
            # This ensures the global cost is not dominated by one outlier segment.
            segment_cost = np.sum(np.abs(y_sub - y_pred))
            total_cost += segment_cost

        except ValueError:
            return np.inf # Catch singular matrices or empty slices

    return total_cost

def _ols_cost_objective(breakpoints, X, y, min_size=5):
    """
    Calculates the total OLS cost (SSE) of a specific breakpoint configuration.
    Used for the baseline comparison.
    """
    bkps = np.unique(breakpoints.astype(int))
    bkps = np.sort(bkps)

    full_bkps = np.concatenate(([0], bkps, [len(y)]))
    segment_lengths = np.diff(full_bkps)

    if np.any(segment_lengths < min_size):
        return np.inf

    total_cost = 0.0
    model = LinearRegression()

    for i in range(len(full_bkps) - 1):
        start, end = full_bkps[i], full_bkps[i+1]
        X_sub = X[start:end].reshape(-1, 1)
        y_sub = y[start:end]

        if len(y_sub) < 2: return np.inf

        try:
            model.fit(X_sub, y_sub)
            y_pred = model.predict(X_sub)
            # Sum of SQUARED Errors for OLS
            segment_cost = np.sum((y_sub - y_pred)**2)
            total_cost += segment_cost
        except ValueError:
            return np.inf

    return total_cost

def find_breakpoints_scout(X, y, n_bkps, bounds_margin=5, cost_func=_huber_cost_objective):
    """
    Uses Global Stochastic Optimization to find approximate breakpoint locations.
    """
    n = len(y)

    # Search space: continuous floats between index [margin] and [n-margin]
    bounds = [(bounds_margin, n - bounds_margin)] * n_bkps

    result = differential_evolution(
        func=cost_func,
        bounds=bounds,
        args=(X, y, bounds_margin),
        strategy='best1bin',     # Standard DE strategy
        maxiter=100,             # Increase to 1000 for N > 5000 if needed
        popsize=15,              # Population size multiplier
        mutation=(0.5, 1.0),     # High mutation helps escape local minima
        recombination=0.7,
        tol=0.01,
        polish=False             # We don't need gradient polishing on discrete indices
    )

    # Return sorted integer indices
    best_bkps = np.sort(np.unique(result.x.astype(int)))
    return best_bkps

def refine_segments(X, y, breakpoints):
    """
    Applies Theil-Sen estimator to finalized segments.
    """
    n = len(y)
    full_bkps = np.concatenate(([0], breakpoints, [n]))

    results = []

    for i in range(len(full_bkps) - 1):
        start, end = full_bkps[i], full_bkps[i+1]

        X_seg = X[start:end]
        y_seg = y[start:end]

        # Store X boundary values for prediction
        x_start_val = X_seg[0] if len(X_seg) > 0 else (X[start] if start < len(X) else X[-1])
        x_end_val = X_seg[-1] if len(X_seg) > 0 else (X[end-1] if end > 0 else X[0])

        if len(y_seg) < 2:
            # Handle edge case of tiny segment
            results.append({
                "segment_id": i,
                "start_idx": start,
                "end_idx": end,
                "x_start": x_start_val,
                "x_end": x_end_val,
                "slope": np.nan,
                "intercept": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan
            })
            continue

        # Theil-Sen: 29.3% Breakdown point
        slope, intercept, lo_slope, hi_slope = theilslopes(y_seg, X_seg, alpha=0.95)

        results.append({
            "segment_id": i,
            "start_idx": start,
            "end_idx": end,
            "x_start": x_start_val,
            "x_end": x_end_val,
            "slope": slope,
            "intercept": intercept,
            "ci_lower": lo_slope,
            "ci_upper": hi_slope
        })

    return results

def refine_segments_ols(X, y, breakpoints):
    """
    Applies OLS estimator to finalized segments (Baseline).
    """
    n = len(y)
    full_bkps = np.concatenate(([0], breakpoints, [n]))

    results = []
    model = LinearRegression()

    for i in range(len(full_bkps) - 1):
        start, end = full_bkps[i], full_bkps[i+1]
        X_seg = X[start:end].reshape(-1, 1)
        y_seg = y[start:end]

        # Store X boundary values for prediction
        x_start_val = X_seg[0] if len(X_seg) > 0 else (X[start] if start < len(X) else X[-1])
        x_end_val = X_seg[-1] if len(X_seg) > 0 else (X[end-1] if end > 0 else X[0])

        if len(y_seg) < 2:
             results.append({
                "segment_id": i,
                "start_idx": start,
                "end_idx": end,
                "x_start": x_start_val,
                "x_end": x_end_val,
                "slope": np.nan,
                "intercept": np.nan,
                "ci_lower": np.nan,
                "ci_upper": np.nan
            })
             continue

        model.fit(X_seg, y_seg)
        slope = model.coef_[0]
        intercept = model.intercept_

        results.append({
            "segment_id": i,
            "start_idx": start,
            "end_idx": end,
            "x_start": x_start_val,
            "x_end": x_end_val,
            "slope": slope,
            "intercept": intercept,
            "ci_lower": np.nan, # OLS CI calculation requires more work, skipping for speed test
            "ci_upper": np.nan
        })

    return results

class RobustSegmentedTrend:
    def __init__(self, n_breakpoints=1):
        self.n_breakpoints = n_breakpoints
        self.breakpoints_ = None
        self.segments_ = None

    def fit(self, X, y):
        # 1. Input Validation
        X = np.asarray(X)
        y = np.asarray(y)
        if len(X) != len(y):
            raise ValueError("X and y must be same length")

        # 2. SCOUT PHASE: Find breakpoints using DE + Huber
        self.breakpoints_ = find_breakpoints_scout(X, y, self.n_breakpoints, cost_func=_huber_cost_objective)

        # 3. REFINE PHASE: Estimate parameters using Theil-Sen
        self.segments_ = refine_segments(X, y, self.breakpoints_)

        return self

    def predict(self, X):
        X = np.asarray(X)
        y_pred = np.zeros_like(X, dtype=float)

        for i, seg in enumerate(self.segments_):
            if np.isnan(seg['slope']): continue

            # Determine mask for this segment
            # For the first segment, include everything <= x_end
            if i == 0:
                mask = (X <= seg['x_end'])
            # For the last segment, include everything >= x_start
            elif i == len(self.segments_) - 1:
                mask = (X >= seg['x_start'])
            # For middle segments, include range [x_start, x_end)
            else:
                mask = (X >= seg['x_start']) & (X < seg['x_end'])

            # Apply linear model
            y_pred[mask] = seg['slope'] * X[mask] + seg['intercept']

        return y_pred

class SimpleSegmentedTrend:
    """Baseline OLS-based Segmented Regression"""
    def __init__(self, n_breakpoints=1):
        self.n_breakpoints = n_breakpoints
        self.breakpoints_ = None
        self.segments_ = None

    def fit(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y)

        # Scout with OLS cost
        self.breakpoints_ = find_breakpoints_scout(X, y, self.n_breakpoints, cost_func=_ols_cost_objective)

        # Refine with OLS
        self.segments_ = refine_segments_ols(X, y, self.breakpoints_)
        return self

    def predict(self, X):
        X = np.asarray(X)
        y_pred = np.zeros_like(X, dtype=float)

        for i, seg in enumerate(self.segments_):
            if np.isnan(seg['slope']): continue

            if i == 0:
                mask = (X <= seg['x_end'])
            elif i == len(self.segments_) - 1:
                mask = (X >= seg['x_start'])
            else:
                mask = (X >= seg['x_start']) & (X < seg['x_end'])

            y_pred[mask] = seg['slope'] * X[mask] + seg['intercept']

        return y_pred
