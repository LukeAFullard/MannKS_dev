import numpy as np
import pandas as pd
from typing import Union, Optional, List, Tuple
from collections import namedtuple
from scipy.stats import norm

from ._segmented import (bootstrap_restart_segmented,
                         get_breakpoint_bootstrap_distribution,
                         _create_segments,
                         _calculate_segment_residuals,
                         find_bagging_breakpoint) # Need this for n=0 SAR calculation if skipped
from .trend_test import trend_test
from ._datetime import _to_numeric_time, _is_datetime_like

def _prepare_data(x, t, hicensor=False):
    """
    Internal helper to prepare data for segmented analysis.
    Avoids dependency on _helpers.py if not needed.
    """
    is_dt = _is_datetime_like(t)
    t_num = _to_numeric_time(t)

    if isinstance(x, pd.DataFrame):
        df = x.copy()
        if 'value' not in df.columns:
             # Fallback: assume single column is value
             if x.shape[1] == 1:
                 df.columns = ['value']
                 df['censored'] = False
                 df['cen_type'] = 'none'
             else:
                 # If prepared by prepare_censored_data, it has correct columns
                 pass
        if 'censored' not in df.columns:
             df['censored'] = False
        if 'cen_type' not in df.columns:
             df['cen_type'] = 'none'
    else:
        df = pd.DataFrame({'value': np.asarray(x)})
        df['censored'] = False
        df['cen_type'] = 'none'

    df['t'] = t_num
    df['t_original'] = np.asarray(t)

    # Handle missing values
    mask = ~np.isnan(df['value'])
    df = df[mask].copy()

    # Sort by time
    df = df.sort_values('t').reset_index(drop=True)

    # HiCensor logic (simplified or full)
    if hicensor:
        # Re-implement simplified HiCensor or assume trend_test handles it?
        # trend_test handles it for segments.
        # But we need it for global breakpoint optimization?
        # If we optimize on raw data, we might be wrong if hicensor changes values.
        # So we should apply it here.
        if isinstance(hicensor, bool) and hicensor:
             if 'lt' in df['cen_type'].values:
                 max_lt = df.loc[df['cen_type'] == 'lt', 'value'].max()
                 mask_hi = df['value'] < max_lt
                 df.loc[mask_hi, 'censored'] = True
                 df.loc[mask_hi, 'cen_type'] = 'lt'
                 df.loc[mask_hi, 'value'] = max_lt
        elif isinstance(hicensor, (int, float)):
             max_lt = hicensor
             mask_hi = df['value'] < max_lt
             df.loc[mask_hi, 'censored'] = True
             df.loc[mask_hi, 'cen_type'] = 'lt'
             df.loc[mask_hi, 'value'] = max_lt

    return df, is_dt

def segmented_trend_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    n_breakpoints: int = 1,
    min_segment_size: int = 10,
    n_bootstrap: int = 200,  # For probability/CI generation
    alpha: float = 0.05,
    hicensor: Union[bool, float] = False,
    criterion: str = 'bic',
    **kwargs
):
    """
    Perform segmented Sen's slope trend analysis.

    Args:
        x: Data vector or DataFrame (if pre-processed).
        t: Time vector.
        n_breakpoints: Number of breakpoints to detect.
        min_segment_size: Minimum number of observations per segment.
        n_bootstrap: Number of bootstrap samples for breakpoint uncertainty.
        alpha: Significance level.
        hicensor: High-censor rule flag.
        criterion: Model selection criterion ('bic' or 'aic'). Default 'bic'.
        **kwargs: Additional arguments passed to trend_test and the Sen's estimator
                  (e.g., lt_mult, sens_slope_method, slope_scaling).

    Returns:
        namedtuple: Segmented_Trend_Test result.
    """
    # 1. Data Prep
    data_filtered, is_datetime = _prepare_data(x, t, hicensor)

    x_val = data_filtered['value'].to_numpy()
    t_numeric = data_filtered['t'].to_numpy()
    censored = data_filtered['censored'].to_numpy()
    cen_type = data_filtered['cen_type'].to_numpy()

    if len(x_val) < 2:
        raise ValueError("Insufficient data for segmented analysis.")

    # 2. Find Optimal Breakpoints
    if n_breakpoints > 0:
        # Pass kwargs (like lt_mult) to the breakpoint search
        # Use a reasonable number of restarts for the point estimate
        n_restarts = min(n_bootstrap, 50)
        breakpoints, converged, best_residual = bootstrap_restart_segmented(
            x_val, t_numeric, censored, cen_type,
            n_breakpoints=n_breakpoints,
            min_segment_size=min_segment_size,
            n_bootstrap=n_restarts,
            **kwargs
        )
    else:
        # No breakpoints (single trend)
        breakpoints = np.array([])
        converged = True
        # Calculate residual for the single segment
        from ._segmented import _calculate_segment_residuals
        best_residual = _calculate_segment_residuals(
            x_val, t_numeric, censored, cen_type, breakpoints, **kwargs
        )

    # Calculate Criterion (BIC or AIC)
    # k = parameters. Independent segments:
    # Each segment has slope and intercept (2 params).
    # Plus breakpoints (n_breakpoints params).
    # Total segments = n_breakpoints + 1
    # k = 2 * (n_breakpoints + 1) + n_breakpoints = 3 * n_breakpoints + 2
    n_obs = len(x_val)
    k = 3 * n_breakpoints + 2

    # Handle zero residual (perfect fit) to avoid log(0)
    if best_residual <= 0:
        safe_residual = 1e-10
    else:
        safe_residual = best_residual

    bic = n_obs * np.log(safe_residual / n_obs) + k * np.log(n_obs)
    aic = n_obs * np.log(safe_residual / n_obs) + 2 * k

    if criterion.lower() == 'aic':
        score = aic
    else:
        score = bic

    # 3. Generate Bootstrap Distribution (For CIs and Probabilities)
    # Only if n_breakpoints > 0 and n_bootstrap > 0
    if n_breakpoints > 0 and n_bootstrap > 0:
        boot_breakpoints_numeric = get_breakpoint_bootstrap_distribution(
            x_val, t_numeric, censored, cen_type, breakpoints,
            n_bootstrap=n_bootstrap,
            **kwargs
        )
    else:
        boot_breakpoints_numeric = np.array([])


    # 4. Analyze Segments (Run trend_test on each piece)
    segments_numeric = _create_segments(t_numeric, breakpoints)
    segment_results = []

    for i, (start, end) in enumerate(segments_numeric):
        # Define mask for segment
        if i == len(segments_numeric) - 1:
             mask = (t_numeric >= start) & (t_numeric <= end)
        else:
             mask = (t_numeric >= start) & (t_numeric < end)

        if np.sum(mask) < 2:
            segment_res = None
        else:
            # Extract subset
            t_sub = t_numeric[mask]
            if is_datetime:
                t_sub_orig = data_filtered.loc[data_filtered.index[mask], 't_original'].values
            else:
                t_sub_orig = t_sub

            df_sub = data_filtered.iloc[mask].copy()
            segment_res = trend_test(df_sub, t_sub_orig, alpha=alpha, hicensor=False, **kwargs)

        segment_results.append(segment_res)

    # 5. Convert numeric breakpoints back to Datetime and Calc CIs
    breakpoint_cis = []
    boot_breakpoints_final = np.array([])

    if n_breakpoints > 0:
        if len(boot_breakpoints_numeric) > 0:
            # Calculate CIs on numeric breakpoints
            ci_lower = np.percentile(boot_breakpoints_numeric, 100 * (alpha / 2), axis=0)
            ci_upper = np.percentile(boot_breakpoints_numeric, 100 * (1 - alpha / 2), axis=0)

            if is_datetime:
                breakpoints_final = pd.to_datetime(breakpoints, unit='s')

                flat_boot = boot_breakpoints_numeric.flatten()
                flat_boot_dt = pd.to_datetime(flat_boot, unit='s')
                boot_breakpoints_final = flat_boot_dt.values.reshape(boot_breakpoints_numeric.shape)

                ci_lower_final = pd.to_datetime(ci_lower, unit='s')
                ci_upper_final = pd.to_datetime(ci_upper, unit='s')
                breakpoint_cis = list(zip(ci_lower_final, ci_upper_final))
            else:
                breakpoints_final = breakpoints
                boot_breakpoints_final = boot_breakpoints_numeric
                breakpoint_cis = list(zip(ci_lower, ci_upper))
        else:
            # No bootstrap samples
            if is_datetime:
                breakpoints_final = pd.to_datetime(breakpoints, unit='s')
            else:
                breakpoints_final = breakpoints
            breakpoint_cis = [(np.nan, np.nan)] * n_breakpoints

    else:
        breakpoints_final = []

    # 6. Construct Result
    Result = namedtuple('Segmented_Trend_Test', [
        'n_breakpoints', 'breakpoints', 'breakpoint_cis', 'bootstrap_samples', 'segments',
        'converged', 'is_datetime', 'sar', 'bic', 'aic', 'score'
    ])

    valid_results = [r for r in segment_results if r is not None]

    return Result(
        n_breakpoints=n_breakpoints,
        breakpoints=breakpoints_final,
        breakpoint_cis=breakpoint_cis,
        bootstrap_samples=boot_breakpoints_final,
        segments=pd.DataFrame(valid_results),
        converged=converged,
        is_datetime=is_datetime,
        sar=best_residual,
        bic=bic,
        aic=aic,
        score=score
    )

def calculate_breakpoint_probability(result, start_date, end_date):
    """
    Calculate the probability that a structural break occurred within a specific window.
    """
    if result.n_breakpoints == 0:
        return 0.0

    samples = result.bootstrap_samples

    # Handle Datetime conversion
    if result.is_datetime:
        start_val = pd.to_datetime(start_date)
        end_val = pd.to_datetime(end_date)
        flat_samples = samples.flatten()
        start_val_np = start_val.to_datetime64()
        end_val_np = end_val.to_datetime64()
    else:
        start_val = float(start_date)
        end_val = float(end_date)
        flat_samples = samples.flatten()
        start_val_np = start_val
        end_val_np = end_val

    in_window = (flat_samples >= start_val_np) & (flat_samples <= end_val_np)
    probability = np.mean(in_window)

    return probability

def find_best_segmentation(
    x, t,
    max_breakpoints=3,
    merge_similar_segments=False,
    merging_alpha=0.05,
    criterion='bic',
    use_permutation_test=False,
    n_permutations=1000,
    **kwargs
):
    """
    Fits segmented models with 0 to max_breakpoints and selects the best one using BIC or AIC.

    Args:
        x, t: Data and time.
        max_breakpoints: Maximum number of breakpoints to test.
        merge_similar_segments (bool): If True, performs an additional check on the
                                       selected model. If adjacent segments do not have
                                       statistically different slopes (based on Z-test),
                                       the model is simplified by falling back to N-1 breakpoints.
        merging_alpha (float): Significance level for the Z-test when merging (default 0.05).
        criterion (str): 'bic' (default) or 'aic'.
        use_permutation_test (bool): If True, uses a permutation test to decide if adding
                                     breakpoints significantly reduces residual error.
        n_permutations (int): Number of permutations for the significance test.
        **kwargs: Arguments passed to segmented_trend_test.

    Returns:
        tuple: (best_result, summary_dataframe)
    """

    # --- Permutation Test Branch ---
    if use_permutation_test:
        from ._segmented import _perform_permutation_test

        # Start with N=0
        current_n = 0
        best_n = 0

        # Calculate N=0 model (Base)
        kwargs_fast = kwargs.copy()
        kwargs_fast['n_bootstrap'] = 0
        kwargs_fast['criterion'] = criterion

        current_model = segmented_trend_test(x, t, n_breakpoints=0, **kwargs_fast)
        models_perm = {0: current_model}

        while current_n < max_breakpoints:
            next_n = current_n + 1

            # Calculate N+1 model
            next_model = segmented_trend_test(x, t, n_breakpoints=next_n, **kwargs_fast)
            models_perm[next_n] = next_model

            # Test Significance (current vs next)
            # Null: current_n (fewer breakpoints) is sufficient
            # Alt: next_n (more breakpoints) is significantly better

            # We need to pass the actual data arrays for permutation
            # _prepare_data is internal, so we call it again or trust helper
            df_prep, _ = _prepare_data(x, t, kwargs.get('hicensor', False))
            x_vals = df_prep['value'].to_numpy()
            t_vals = df_prep['t'].to_numpy()
            censored = df_prep['censored'].to_numpy()
            cen_type = df_prep['cen_type'].to_numpy()

            p_value = _perform_permutation_test(
                x_vals, t_vals, censored, cen_type,
                base_sar=current_model.sar,
                alt_sar=next_model.sar,
                n_breakpoints_base=current_n,
                n_breakpoints_alt=next_n,
                n_permutations=n_permutations,
                **kwargs
            )

            if p_value < merging_alpha: # Use merging_alpha as significance threshold? Or separate?
                # Let's use standard alpha or reusing merging_alpha for consistency in "strictness"
                # If significant, we accept the new breakpoint and continue looking
                best_n = next_n
                current_n = next_n
                current_model = next_model
            else:
                # Not significant improvement, stop here
                break

        # Now we have best_n decided by permutation test.
        # Proceed to bootstrap final model if requested.
        user_n_boot = kwargs.get('n_bootstrap', 200)
        if user_n_boot > 0 and best_n > 0:
            final_result = segmented_trend_test(x, t, n_breakpoints=best_n, criterion=criterion, **kwargs)
        else:
            final_result = models_perm[best_n]

        # Create a summary compatible with the function return (even if fake)
        summary_list = []
        for n, mod in models_perm.items():
            summary_list.append({
                'n_breakpoints': n,
                'bic': mod.bic,
                'aic': mod.aic,
                'score': mod.score,
                'sar': mod.sar,
                'converged': mod.converged
            })
        summary = pd.DataFrame(summary_list)

        return final_result, summary

    # --- Standard AIC/BIC Branch ---

    results_list = []
    models = []

    for n in range(max_breakpoints + 1):
        try:
            # Run without bootstrap first for speed
            # Copy kwargs and set n_bootstrap=0
            kwargs_fast = kwargs.copy()
            kwargs_fast['n_bootstrap'] = 0
            kwargs_fast['criterion'] = criterion # Pass criterion

            res = segmented_trend_test(x, t, n_breakpoints=n, **kwargs_fast)
            models.append(res)
            results_list.append({
                'n_breakpoints': n,
                'bic': res.bic,
                'aic': res.aic,
                'score': res.score,
                'sar': res.sar,
                'converged': res.converged
            })
        except Exception as e:
            results_list.append({
                'n_breakpoints': n,
                'bic': np.inf,
                'aic': np.inf,
                'score': np.inf,
                'sar': np.inf,
                'converged': False,
                'error': str(e)
            })
            models.append(None)

    summary = pd.DataFrame(results_list)

    # Select best model (min Score)
    # Filter out failed models
    valid_summary = summary[summary['converged'] == True]
    if valid_summary.empty:
        raise RuntimeError("No models converged.")

    # Sort by Score to find the initial best candidate
    best_n_idx = valid_summary['score'].idxmin()
    best_n = valid_summary.loc[best_n_idx, 'n_breakpoints']

    user_n_boot = kwargs.get('n_bootstrap', 200)

    # Optional: Merge/Simplify Check
    # If the user wants to remove "spurious" breakpoints where slopes are not sig. diff.
    if merge_similar_segments and best_n > 0:
        current_n = best_n

        # We iterate downwards. If we reject 'current_n', we fall back to 'current_n - 1'.
        while current_n > 0:
            # We must compute the full result (with CIs) to check overlap.
            # If models[current_n] was computed without bootstrap, we must re-compute.
            # However, we'll re-compute anyway to be safe and use user's n_bootstrap.

            if user_n_boot > 0:
                candidate_res = segmented_trend_test(x, t, n_breakpoints=current_n, criterion=criterion, **kwargs)
            else:
                # If no bootstrap, we can't check CIs. We cannot perform the merge check.
                # Since user requested merge_similar_segments, this is a conflict.
                best_n = current_n
                best_result = models[current_n]
                break

            segments = candidate_res.segments
            valid_segments = True

            # Check adjacent pairs for difference
            if segments is not None and not segments.empty:
                for i in range(len(segments) - 1):
                    try:
                        # Extract Slopes and CI bounds
                        s1 = segments.iloc[i]['slope']
                        l1 = segments.iloc[i]['lower_ci']
                        u1 = segments.iloc[i]['upper_ci']

                        s2 = segments.iloc[i+1]['slope']
                        l2 = segments.iloc[i+1]['lower_ci']
                        u2 = segments.iloc[i+1]['upper_ci']

                        # Handle NaNs
                        if pd.isna(s1) or pd.isna(l1) or pd.isna(u1) or \
                           pd.isna(s2) or pd.isna(l2) or pd.isna(u2):
                            valid_segments = False # Can't prove distinct
                            break

                        # Z-Test for Difference
                        # Estimate SE = (Upper - Lower) / (2 * Z_crit)
                        # We assume 95% CI implies Z_crit ~ 1.96
                        # This works regardless of user's 'alpha' if we consistently un-standardize.
                        # However, strictly, if user provided alpha=0.10, the range is 1.645 sigma.
                        # We should use the Z corresponding to the alpha used in trend_test.

                        # Get user alpha from kwargs or default 0.05
                        test_alpha = kwargs.get('alpha', 0.05)
                        z_crit = norm.ppf(1 - test_alpha / 2)

                        se1 = (u1 - l1) / (2 * z_crit)
                        se2 = (u2 - l2) / (2 * z_crit)

                        # Pooled SE for difference
                        se_diff = np.sqrt(se1**2 + se2**2)

                        if se_diff == 0:
                             # Should not happen with bootstrap unless identical resamples
                             # If slopes are diff, Z is inf -> distinct. If slopes same, Z=0 -> merge.
                             if s1 != s2:
                                 z_stat = np.inf
                             else:
                                 z_stat = 0
                        else:
                            z_stat = (s1 - s2) / se_diff

                        p_val = 2 * (1 - norm.cdf(abs(z_stat)))

                        # Null Hypothesis: Slopes are equal.
                        # If p_val > merging_alpha, we Fail to Reject H0. -> Slopes are similar -> Merge (Invalid Segments)
                        # If p_val < merging_alpha, we Reject H0. -> Slopes are different -> Keep.

                        if p_val > merging_alpha:
                            valid_segments = False # Found a pair that is "similar"
                            break

                    except Exception:
                        pass

            if valid_segments:
                # This model is valid (all adjacent slopes are distinct)
                best_n = current_n
                best_result = candidate_res
                break
            else:
                # Reject this N, try N-1
                current_n -= 1

        if current_n == 0:
            best_n = 0
            best_result = models[0]

    else:
        # Standard logic: Re-run best model with full bootstrap if needed
        if user_n_boot > 0 and best_n > 0:
            best_result = segmented_trend_test(x, t, n_breakpoints=best_n, criterion=criterion, **kwargs)
        else:
            best_result = models[best_n]

    return best_result, summary
