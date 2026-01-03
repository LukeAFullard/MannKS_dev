import numpy as np
import pandas as pd
from typing import Union, Optional, List, Tuple
from collections import namedtuple
from ._segmented import (bootstrap_restart_segmented,
                         get_breakpoint_bootstrap_distribution,
                         _create_segments,
                         _calculate_segment_residuals) # Need this for n=0 SAR calculation if skipped
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

    # Calculate BIC
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
    # Also calculate RSS equivalent? SAR is L1 norm.
    # BIC formula assumes likelihood. For Laplace (L1), -2*ln(L) = 2 * SAR / scale?
    # Common approx for L1: n * ln(SAR/n) + k * ln(n) (assuming scale is estimated)
    # We use this proxy.

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
        'converged', 'is_datetime', 'sar', 'bic'
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
        bic=bic
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

def find_best_segmentation(x, t, max_breakpoints=3, **kwargs):
    """
    Fits segmented models with 0 to max_breakpoints and selects the best one using BIC.

    Args:
        x, t: Data and time.
        max_breakpoints: Maximum number of breakpoints to test.
        **kwargs: Arguments passed to segmented_trend_test.

    Returns:
        tuple: (best_result, summary_dataframe)
    """
    results_list = []
    models = []

    for n in range(max_breakpoints + 1):
        try:
            # Run without bootstrap first for speed
            # Copy kwargs and set n_bootstrap=0
            kwargs_fast = kwargs.copy()
            kwargs_fast['n_bootstrap'] = 0

            res = segmented_trend_test(x, t, n_breakpoints=n, **kwargs_fast)
            models.append(res)
            results_list.append({
                'n_breakpoints': n,
                'bic': res.bic,
                'sar': res.sar,
                'converged': res.converged
            })
        except Exception as e:
            results_list.append({
                'n_breakpoints': n,
                'bic': np.inf,
                'sar': np.inf,
                'converged': False,
                'error': str(e)
            })
            models.append(None)

    summary = pd.DataFrame(results_list)

    # Select best model (min BIC)
    # Filter out failed models
    valid_summary = summary[summary['converged'] == True]
    if valid_summary.empty:
        raise RuntimeError("No models converged.")

    best_n = valid_summary.loc[valid_summary['bic'].idxmin(), 'n_breakpoints']

    # If the user requested n_bootstrap > 0, we should rerun the best model with full bootstrap
    user_n_boot = kwargs.get('n_bootstrap', 200)
    if user_n_boot > 0 and best_n > 0:
        # Re-run best model with full bootstrap
        best_result = segmented_trend_test(x, t, n_breakpoints=best_n, **kwargs)
    else:
        best_result = models[best_n]

    return best_result, summary
