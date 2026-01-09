import numpy as np
import pandas as pd
from typing import Union, Optional, List, Tuple
from ._stats import _sens_estimator_unequal_spacing, _sens_estimator_censored
from ._datetime import _to_numeric_time

def _create_segments(t, breakpoints):
    """Create segment boundaries from breakpoints."""
    try:
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
    except Exception as e:
        # Re-raise to be handled by caller, but log if needed in future
        raise

def _calculate_segment_residuals(x, t, censored, cen_type, breakpoints, return_fitted=False, continuity=True, **kwargs):
    """
    Calculate sum of absolute residuals for continuous segmented model.
    Uses Sen's slopes for segments and a robust global intercept.

    If return_fitted=True, returns (total_residual, y_fitted).
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
            if return_fitted:
                return np.inf, None
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
             if return_fitted:
                return np.inf, None
             return np.inf
        slopes.append(slope_est)

    if continuity:
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

            if return_fitted:
                return total_residual, y_fitted
        else:
            total_residual = np.inf
            if return_fitted:
                return np.inf, None
    else:
        # INDEPENDENT SEGMENTS (Discontinuous)
        y_fitted = np.zeros_like(x)
        total_residual = 0.0
        sorted_bp = np.sort(breakpoints)
        boundaries = [np.min(t)] + list(sorted_bp) + [np.max(t)]

        for i in range(len(slopes)):
            t_start = boundaries[i]
            t_end = boundaries[i+1]

            # Mask logic
            if i == len(slopes) - 1:
                 mask = (t >= t_start) & (t <= t_end)
            else:
                 mask = (t >= t_start) & (t < t_end)

            # Get segment data
            x_seg = x[mask]
            t_seg = t[mask]
            cen_seg = censored[mask]

            slope = slopes[i]

            # Estimate Intercept for this segment independently
            # intercept = median(x - slope*t)
            if np.any(~cen_seg):
                resid_raw = x_seg - slope * t_seg
                intercept = np.median(resid_raw[~cen_seg])
            else:
                intercept = 0.0 # Cannot estimate if all censored

            y_fit_seg = slope * t_seg + intercept
            y_fitted[mask] = y_fit_seg

            # Calc residuals
            if np.any(~cen_seg):
                seg_resids = np.abs(x_seg[~cen_seg] - y_fit_seg[~cen_seg])
                total_residual += np.sum(seg_resids)

        if return_fitted:
            return total_residual, y_fitted

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
        if n_breakpoints > 0:
            t_range = np.max(t) - np.min(t)
            start_values = [np.min(t) + (i+1) * t_range / (n_breakpoints + 1)
                            for i in range(n_breakpoints)]
        else:
            start_values = []

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
        if n_breakpoints > 0:
            if np.max(np.abs(breakpoints - breakpoints_old)) < tol:
                return breakpoints, True
        else:
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

    # Clean kwargs to remove parameters that shouldn't be propagated recursively or cause duplicates
    # n_bootstrap is consumed here, so we remove it from kwargs passed to children
    # criterion is not used by segmented_sens_slope or _calculate_segment_residuals
    # merging_alpha is not used here
    kwargs_clean = kwargs.copy()
    kwargs_clean.pop('n_bootstrap', None)
    kwargs_clean.pop('criterion', None)
    kwargs_clean.pop('merging_alpha', None)
    kwargs_clean.pop('use_permutation_test', None)
    kwargs_clean.pop('n_permutations', None)

    best_residual = np.inf
    best_breakpoints = None
    best_converged = False

    # Try Grid Search + 5 random starts + n_bootstrap resamples
    # We use fewer attempts if data is small to save time
    n_attempts = 5 + n_bootstrap

    t_min = np.min(t)
    t_max = np.max(t)

    # 0. Grid Search Initialization (for robustness in noisy data)
    # Especially for n_breakpoints=1, a grid search is cheap and prevents getting stuck
    grid_best_bp = None
    if n_breakpoints == 1:
        grid_size = 20
        buffer = (t_max - t_min) * 0.1
        # Search inner 80%
        grid_points = np.linspace(t_min + buffer, t_max - buffer, grid_size)

        # We perform a quick check of residuals for each grid point
        # This acts as a "coarse" search
        grid_best_resid = np.inf

        for gp in grid_points:
            test_bp = np.array([gp])
            # Quick check (no optimization yet, just evaluation)
            resid = _calculate_segment_residuals(x, t, censored, cen_type, test_bp, min_segment_size=min_segment_size, **kwargs_clean)
            if resid < grid_best_resid:
                grid_best_resid = resid
                grid_best_bp = test_bp

        # We will use this best grid point as one of our starts below

    for i in range(n_attempts):
        start_vals = None
        if i == 0 and grid_best_bp is not None:
            # Run 1: Best Grid Point (Deterministic)
            x_run, t_run, cen_run, centype_run = x, t, censored, cen_type
            start_vals = grid_best_bp
        elif i < 5:
            # Run 2-5: Random starts (Stochastic)
            # Use actual data with random start points
            x_run, t_run, cen_run, centype_run = x, t, censored, cen_type

            if n_breakpoints > 0:
                # Random starts within inner 80% of data to avoid edges
                buffer = (t_max - t_min) * 0.1
                start_vals = np.sort(np.random.uniform(t_min + buffer, t_max - buffer, n_breakpoints))
            else:
                start_vals = []

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
                                        **kwargs_clean)

        # Evaluate found breakpoints on ORIGINAL data
        resid = _calculate_segment_residuals(x, t, censored, cen_type, bp, min_segment_size=min_segment_size, **kwargs_clean)

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

    # Clean kwargs
    kwargs_clean = kwargs.copy()
    kwargs_clean.pop('n_bootstrap', None)
    kwargs_clean.pop('criterion', None)
    kwargs_clean.pop('merging_alpha', None)
    kwargs_clean.pop('use_permutation_test', None)
    kwargs_clean.pop('n_permutations', None)

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
                                     **kwargs_clean)
        boot_dist.append(bp)

    return np.array(boot_dist)

def _perform_permutation_test(x, t, censored, cen_type, base_sar, alt_sar,
                              n_breakpoints_base, n_breakpoints_alt,
                              n_permutations=1000, **kwargs):
    """
    Perform a permutation test to check if adding breakpoints significantly reduces residual error.

    Logic:
    1. Get residuals from the BASE model (N breakpoints).
    2. Permute residuals randomly.
    3. Add permuted residuals to the BASE model's fitted values to create synthetic data.
    4. Fit the ALT model (N+1 breakpoints) to this synthetic data.
    5. Calculate the reduction in SAR (Base_SAR - Alt_SAR) for the synthetic data.
    6. Compare Observed Reduction with the distribution of Permuted Reductions.

    Args:
        base_sar: SAR of the base model on real data.
        alt_sar: SAR of the alt model on real data.
        n_breakpoints_base: Number of breakpoints in base model.
        n_breakpoints_alt: Number of breakpoints in alt model.

    Returns:
        p_value: Probability that the observed reduction is due to chance.
    """
    observed_reduction = base_sar - alt_sar

    if observed_reduction <= 0:
        return 1.0 # No improvement, definitely not significant

    # We need to re-fit the BASE model to get fitted values (y_hat)
    # We assume 'bootstrap_restart_segmented' or 'segmented_sens_slope' logic was used to get best params.
    # But here we don't have the params passed in, just the SAR.
    # To be precise, we should fit the base model again here to get parameters.
    # Since we don't know the exact breakpoints used for base_sar, we re-optimize.
    # This might result in slightly different SAR if optimization is stochastic, but it's consistent.

    # clean kwargs for recursive calls
    kwargs_clean = kwargs.copy()
    kwargs_clean.pop('n_bootstrap', None)
    kwargs_clean.pop('criterion', None)
    kwargs_clean.pop('merging_alpha', None)
    kwargs_clean.pop('use_permutation_test', None)
    kwargs_clean.pop('n_permutations', None)

    # 1. Fit Base Model to get Fitted Values and Residuals
    # Use fewer restarts for speed here as we just need a good fit
    bp_base, _, _ = bootstrap_restart_segmented(x, t, censored, cen_type,
                                                n_breakpoints=n_breakpoints_base,
                                                n_bootstrap=5, **kwargs_clean)

    _, y_fitted_base = _calculate_segment_residuals(x, t, censored, cen_type, bp_base,
                                                    return_fitted=True, **kwargs_clean)

    if y_fitted_base is None:
        return 1.0 # Failed to fit base model

    residuals_base = x - y_fitted_base # Simple diff, okay for censored?
    # For censored data, residuals are tricky.
    # If censored, y_fitted might not be "true" y.
    # Permutation tests for censored data usually involve permuting survival residuals or similar.
    # Given we are using L1 norm (Sen's slope), permuting simple residuals of observed data
    # is a reasonable approx if censoring is light. If heavy censoring, this is invalid.
    # However, for this implementation, we assume residuals of (value - fit).

    perm_reductions = []

    for _ in range(n_permutations):
        # 2. Permute Residuals
        resid_perm = np.random.permutation(residuals_base)

        # 3. Synthetic Data
        y_synth = y_fitted_base + resid_perm

        # 4. Fit Base and Alt models to Synthetic Data
        # We need to calculate SAR improvement on this synthetic data
        # Note: We must re-fit BOTH Base and Alt on synthetic data to see how much Alt improves over Base
        # strictly due to flexibility, not due to signal.

        # Fit Base on Synthetic
        _, _, sar_base_synth = bootstrap_restart_segmented(y_synth, t, censored, cen_type,
                                                           n_breakpoints=n_breakpoints_base,
                                                           n_bootstrap=0, **kwargs_clean) # Fast fit

        # Fit Alt on Synthetic
        _, _, sar_alt_synth = bootstrap_restart_segmented(y_synth, t, censored, cen_type,
                                                          n_breakpoints=n_breakpoints_alt,
                                                          n_bootstrap=0, **kwargs_clean) # Fast fit

        perm_reduction = sar_base_synth - sar_alt_synth
        perm_reductions.append(perm_reduction)

    perm_reductions = np.array(perm_reductions)

    # 5. Calculate P-Value
    # P = (Number of perm_reductions >= observed_reduction) / n_permutations
    p_value = np.mean(perm_reductions >= observed_reduction)

    return p_value

def find_bagging_breakpoint(x, t, censored, cen_type,
                           n_breakpoints=1,
                           n_bootstrap=100,
                           aggregation='median',
                           **kwargs):
    """
    Estimate breakpoint locations using Bagging (Bootstrap Aggregating).

    This method generates 'n_bootstrap' resamples of the data, finds the optimal
    breakpoints for each resample, and then aggregates these estimates to provide
    a robust breakpoint location.

    Args:
        x, t: Data arrays.
        censored, cen_type: Censoring information.
        n_breakpoints: Number of breakpoints to detect.
        n_bootstrap: Number of bootstrap samples.
        aggregation: Method to aggregate bootstrap results ('median' or 'mean').
        **kwargs: Arguments passed to the breakpoint search function.

    Returns:
        bagged_breakpoints: The aggregated breakpoint locations (numeric).
    """
    # Clean kwargs
    kwargs_clean = kwargs.copy()
    kwargs_clean.pop('n_bootstrap', None)
    kwargs_clean.pop('criterion', None)

    n = len(x)
    all_breakpoints = []

    # Initial Robust Estimate (Warm Start)
    # Perform a global search on the original dataset once.
    initial_bp, _, _ = bootstrap_restart_segmented(
        x, t, censored, cen_type,
        n_breakpoints=n_breakpoints,
        n_bootstrap=0, # Use 0 bootstrap restarts for the initial global search (Grid + 5 random)
        **kwargs_clean
    )

    for _ in range(n_bootstrap):
        # Bootstrap Resample (Pairs bootstrap)
        idx = np.random.choice(n, n, replace=True)
        x_boot = x[idx]
        t_boot = t[idx]
        cen_boot = censored[idx]
        cen_type_boot = cen_type[idx]

        # Find breakpoints for this sample
        # Use Warm-Started Optimization:
        # Instead of a full global search, we start the local optimizer at the
        # robust estimate found on the full dataset. This assumes the bootstrap
        # samples will have solutions close to the population solution.
        bp, _ = segmented_sens_slope(
            x_boot, t_boot, cen_boot, cen_type_boot,
            n_breakpoints=n_breakpoints,
            start_values=initial_bp, # Pass the robust estimate as warm start
            **kwargs_clean
        )
        all_breakpoints.append(bp)

    all_breakpoints = np.array(all_breakpoints)

    # Aggregate
    # For multiple breakpoints, we need to ensure we aggregate "corresponding" breakpoints.
    # Since 'segmented_sens_slope' returns sorted breakpoints, bp[0] is always the first, etc.
    # So column-wise aggregation is valid.
    if aggregation == 'mean':
        final_bp = np.nanmean(all_breakpoints, axis=0)
    else:
        final_bp = np.nanmedian(all_breakpoints, axis=0)

    return final_bp
