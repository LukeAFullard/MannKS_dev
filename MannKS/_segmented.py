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
    Calculate sum of absolute residuals for segmented model.
    Uses Sen's slope for robust estimation (L1 norm equivalent).
    """
    segments = _create_segments(t, breakpoints)
    total_residual = 0

    # Extract kwargs for _sens_estimator_censored
    lt_mult = kwargs.get('lt_mult', 0.5)
    gt_mult = kwargs.get('gt_mult', 1.1)
    sens_slope_method = kwargs.get('sens_slope_method', 'nan')
    min_segment_size = kwargs.get('min_segment_size', 3) # Default safety lower bound

    for seg_start, seg_end in segments:
        # Use a slightly more robust mask to handle floating point edges
        # We assume left-inclusive, right-exclusive [start, end) except for last point?
        # Actually standard for segments is usually [start, end)
        # But we need to make sure we cover all points.
        # Let's stick to simple >= and <, but handle the very last point separately or ensure t_max is included.
        # However, _create_segments uses t_max as the end of the last segment.
        # If t == t_max, (t < seg_end) will be false for the last segment.
        # Let's adjust the mask for the last segment.

        if seg_end == np.max(t):
             mask = (t >= seg_start) & (t <= seg_end)
        else:
             mask = (t >= seg_start) & (t < seg_end)

        if np.sum(mask) < min_segment_size:
            # Penalize segments with too few points to discourage them
            total_residual += np.inf
            continue

        x_seg = x[mask]
        t_seg = t[mask]
        cen_seg = censored[mask]
        cen_type_seg = cen_type[mask]

        # Estimate Sen's slope for this segment
        if np.any(cen_seg):
            slopes = _sens_estimator_censored(x_seg, t_seg, cen_type_seg,
                                              lt_mult=lt_mult, gt_mult=gt_mult, method=sens_slope_method)
        else:
            slopes = _sens_estimator_unequal_spacing(x_seg, t_seg)

        slope = np.nanmedian(slopes)

        if np.isnan(slope):
             total_residual += np.inf
             continue

        # Calculate fitted values (Robust centering on median)
        t_center = np.median(t_seg)
        # Intercept proxy: median of y minus slope*median(t)
        # We calculate intercept based on non-censored data residuals if possible,
        # or robustly. The guide used median of (x - slope*t).

        # Guide code: x_fitted = np.median(x_seg[~cen_seg]) + slope * (t_seg - t_center)
        # This implies intercept is at t_center.
        # Let's follow the guide logic, but handle all-censored case.

        if np.any(~cen_seg):
             x_median_obs = np.median(x_seg[~cen_seg])
             # The intercept at t_center is x_median_obs.
             # So fitted line passes through (t_center, x_median_obs) with slope.
             # y = y_center + m(t - t_center)
             x_fitted = x_median_obs + slope * (t_seg - t_center)

             # Sum absolute residuals (Robust metric) on observed data
             residuals = np.abs(x_seg[~cen_seg] - x_fitted[~cen_seg])
             total_residual += np.sum(residuals)
        else:
             # If segment is all censored, we can't easily calculate residuals.
             # Penalize? Or use censored values proxy?
             # For now, let's skip/penalize to avoid empty segments being valid.
             total_residual += np.inf

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
