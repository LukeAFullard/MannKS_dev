import numpy as np
import pandas as pd
from typing import Union, Optional, List, Tuple
from ._stats import _sens_estimator_unequal_spacing, _sens_estimator_censored
from ._datetime import _to_numeric_time

def _create_segments(t, breakpoints):
    """Create segment boundaries from breakpoints."""
    t_min, t_max = np.min(t), np.max(t)
    sorted_bp = np.sort(breakpoints)
    segments = []

    if len(sorted_bp) == 0:
        # No breakpoints, single segment covering full range
        return [(t_min, t_max)]

    # First segment
    segments.append((t_min, sorted_bp[0]))

    # Middle segments
    for i in range(len(sorted_bp) - 1):
        segments.append((sorted_bp[i], sorted_bp[i+1]))

    # Last segment
    segments.append((sorted_bp[-1], t_max))

    return segments

def _calculate_segment_residuals(x, t, censored, cen_type, breakpoints, **kwargs):
    """
    Calculate sum of absolute residuals for continuous segmented model.
    Uses Sen's slopes for segments and a robust global intercept.
    """
    segments = _create_segments(t, breakpoints)

    # Extract kwargs for _sens_estimator_censored
    lt_mult = kwargs.get('lt_mult', 0.5)
    gt_mult = kwargs.get('gt_mult', 1.1)
    sens_slope_method = kwargs.get('sens_slope_method', 'nan')
    min_segment_size = kwargs.get('min_segment_size', 3)

    # 1. Estimate Slopes for each segment
    slopes = []

    for i, (seg_start, seg_end) in enumerate(segments):
        # Handle last segment inclusive bound
        if i == len(segments) - 1:
             mask = (t >= seg_start) & (t <= seg_end)
        else:
             mask = (t >= seg_start) & (t < seg_end)

        if np.sum(mask) < min_segment_size:
            return np.inf

        x_seg = x[mask]
        t_seg = t[mask]
        cen_seg = censored[mask]
        cen_type_seg = cen_type[mask]

        if np.any(cen_seg):
            s_vals = _sens_estimator_censored(x_seg, t_seg, cen_type_seg,
                                              lt_mult=lt_mult, gt_mult=gt_mult, method=sens_slope_method)
        else:
            s_vals = _sens_estimator_unequal_spacing(x_seg, t_seg)

        slope_est = np.nanmedian(s_vals)
        if np.isnan(slope_est):
             return np.inf
        slopes.append(slope_est)

    # 2. Construct Continuous Model Function (without intercept)
    # y_shape(t) = Integral of slope(t) dt
    # F(t) = Sum(slope_j * (min(t, bp_j+1) - max(t, bp_j))) effectively.
    # We can compute it vector-wise.

    y_shape = np.zeros_like(t)
    sorted_bp = np.sort(breakpoints)
    boundaries = [np.min(t)] + list(sorted_bp) + [np.max(t)]

    # We define the shape relative to t_min = 0 for the shape function
    # F(t) = slope_0 * (t - t0)   for t in seg 0
    # F(t) = slope_0 * (t1 - t0) + slope_1 * (t - t1)  for t in seg 1
    # etc.

    cumulative_y = 0.0

    for i in range(len(slopes)):
        t_start = boundaries[i]
        t_end = boundaries[i+1]

        # Mask for points in this segment
        if i == len(slopes) - 1:
             mask = (t >= t_start) & (t <= t_end)
        else:
             mask = (t >= t_start) & (t < t_end)

        # Contribution for points in this segment
        # y = cumulative_y_at_start + slope * (t - t_start)
        y_shape[mask] = cumulative_y + slopes[i] * (t[mask] - t_start)

        # Update cumulative_y for next segment start
        cumulative_y += slopes[i] * (t_end - t_start)

    # 3. Estimate Robust Global Intercept
    # We want y = y_shape + Intercept
    # Intercept = median(y - y_shape)
    # Only use uncensored data for intercept estimation
    if np.any(~censored):
        residuals_raw = x - y_shape
        intercept = np.median(residuals_raw[~censored])

        # 4. Calculate Final Residuals
        y_fitted = y_shape + intercept
        final_residuals = np.abs(x[~censored] - y_fitted[~censored])
        total_residual = np.sum(final_residuals)
    else:
        total_residual = np.inf

    return total_residual

def segmented_sens_slope(x, t, censored, cen_type,
                         n_breakpoints=1,
                         start_values=None,
                         max_iter=30,
                         tol=1e-6,
                         min_segment_size=10,
                         **kwargs):
    """
    Iterative algorithm to find optimal breakpoints using robust residuals.
    """
    n = len(x)

    # Initialize breakpoints evenly if not provided
    if start_values is None:
        t_range = np.max(t) - np.min(t)
        start_values = [np.min(t) + (i+1) * t_range / (n_breakpoints + 1)
                        for i in range(n_breakpoints)]

    breakpoints = np.array(start_values, dtype=float)
    t_min_global = np.min(t)
    t_max_global = np.max(t)

    for iteration in range(max_iter):
        breakpoints_old = breakpoints.copy()

        # Optimize each breakpoint individually
        for bp_idx in range(n_breakpoints):
            current_bp = breakpoints[bp_idx]

            # constrain search area to between neighbor breakpoints
            if bp_idx > 0:
                lower_bound = breakpoints[bp_idx - 1]
            else:
                lower_bound = t_min_global

            if bp_idx < n_breakpoints - 1:
                upper_bound = breakpoints[bp_idx + 1]
            else:
                upper_bound = t_max_global

            # Enforce min_segment_size (time buffer)
            t_sorted = np.sort(t)
            if min_segment_size < len(t):
                 # Ensure at least min_segment_size points on either side
                 # If we split at BP, left segment is [min, BP).
                 # To have N points, BP must be > t_sorted[N-1].
                 # Let's say BP >= t_sorted[min_segment_size].
                 valid_min = t_sorted[min_segment_size]

                 # Right segment is [BP, max].
                 # To have N points, BP must be <= t_sorted[n - min_segment_size].
                 valid_max = t_sorted[-min_segment_size]

                 lower_bound = max(lower_bound, valid_min)
                 upper_bound = min(upper_bound, valid_max)

            if lower_bound >= upper_bound:
                continue # Constrained too tightly, skip update

            # Iterative Grid Refinement for better breakpoint location
            # (Robust methods use grid search over derivative-based methods)
            # We refine the grid to avoid "chattering" and find precise optimum

            # Initialize with current position
            best_local_bp = current_bp
            # Calculate current residual if not known?
            # We can calculate it, or assume inf and let search find better.
            # Calculating it ensures we don't worsen the solution.
            test_breakpoints_curr = breakpoints.copy()
            test_breakpoints_curr[bp_idx] = current_bp
            best_local_resid = _calculate_segment_residuals(x, t, censored, cen_type, test_breakpoints_curr, min_segment_size=min_segment_size, **kwargs)

            search_lower = lower_bound
            search_upper = upper_bound

            # 3 passes of 10 points allows focusing the search
            for _ in range(3):
                search_grid = np.linspace(search_lower, search_upper, 10)

                found_better_in_pass = False
                for test_bp in search_grid:
                    test_breakpoints = breakpoints.copy()
                    test_breakpoints[bp_idx] = test_bp
                    resid = _calculate_segment_residuals(x, t, censored, cen_type, test_breakpoints, min_segment_size=min_segment_size, **kwargs)

                    if resid < best_local_resid:
                        best_local_resid = resid
                        best_local_bp = test_bp
                        found_better_in_pass = True

                # Narrow search range around the best point found
                # Current grid spacing
                grid_step = (search_upper - search_lower) / 9.0 if (search_upper > search_lower) else 0

                if grid_step < tol:
                    break

                # New bounds: +/- 1 step around best
                search_lower = max(lower_bound, best_local_bp - grid_step)
                search_upper = min(upper_bound, best_local_bp + grid_step)

            breakpoints[bp_idx] = best_local_bp

        # Check convergence
        if np.max(np.abs(breakpoints - breakpoints_old)) < tol:
            return breakpoints, True

    return breakpoints, False

def bootstrap_restart_segmented(x, t, censored, cen_type,
                                n_breakpoints=1,
                                n_bootstrap=10,
                                min_segment_size=10,
                                **kwargs):
    """
    Randomized restart to avoid local optima (common in segmented regression).
    """
    best_residual = np.inf
    best_breakpoints = None
    best_converged = False

    # Try 5 random starts + n_bootstrap resamples
    # We use fewer attempts if data is small to save time
    n_attempts = 5 + n_bootstrap

    t_min = np.min(t)
    t_max = np.max(t)

    for i in range(n_attempts):
        if i < 5:
            # Use actual data with random start points
            x_run, t_run, cen_run, centype_run = x, t, censored, cen_type
            # Random starts within inner 80% of data to avoid edges
            buffer = (t_max - t_min) * 0.1
            start_vals = np.sort(np.random.uniform(t_min + buffer, t_max - buffer, n_breakpoints))
        else:
            # Bootstrap resample the data
            idx = np.random.choice(len(x), len(x), replace=True)
            # Sort by time to keep segmented logic simpler?
            # Standard bootstrap for regression pairs (x,t) is fine,
            # but for segmented regression on time series, we usually resample residuals or blocks.
            # However, the guide says: "idx = np.random.choice(len(x), len(x), replace=True)"
            # This is a pairs bootstrap.
            x_run, t_run, cen_run, centype_run = x[idx], t[idx], censored[idx], cen_type[idx]
            start_vals = None # Let function pick even starts

        bp, conv = segmented_sens_slope(x_run, t_run, cen_run, centype_run,
                                        n_breakpoints, start_values=start_vals,
                                        min_segment_size=min_segment_size,
                                        **kwargs)

        # Evaluate found breakpoints on ORIGINAL data
        resid = _calculate_segment_residuals(x, t, censored, cen_type, bp, min_segment_size=min_segment_size, **kwargs)

        if resid < best_residual:
            best_residual = resid
            best_breakpoints = bp
            best_converged = conv

    return best_breakpoints, best_converged, best_residual

def get_breakpoint_bootstrap_distribution(x, t, censored, cen_type,
                                         final_breakpoints,
                                         n_bootstrap=200,
                                         **kwargs):
    """
    Generate bootstrap distribution of breakpoints for confidence/probability estimation.

    Returns:
        boot_breakpoints: Array of shape (n_bootstrap, n_breakpoints)
    """
    n = len(x)
    boot_dist = []

    for _ in range(n_bootstrap):
        idx = np.random.choice(n, n, replace=True)
        # Note: For time series, block bootstrap is often better, but we follow the guide's
        # standard pairs bootstrap for now as requested.

        # We start the search at the "optimal" breakpoints found previously
        # This assumes the bootstrap dist is centered near the estimate (Warm start)
        bp, _ = segmented_sens_slope(x[idx], t[idx], censored[idx], cen_type[idx],
                                     n_breakpoints=len(final_breakpoints),
                                     start_values=final_breakpoints,
                                     **kwargs)
        boot_dist.append(bp)

    return np.array(boot_dist)
