import numpy as np
import pandas as pd
from typing import Union, Optional
import warnings
from .trend_test import trend_test
from .seasonal_trend_test import seasonal_trend_test
from ._datetime import _is_datetime_like

def rolling_trend_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    window: Union[str, int, float],
    step: Optional[Union[str, int, float]] = None,
    min_size: int = 10,
    alpha: float = 0.05,
    seasonal: bool = False,
    period: int = 12,
    season_type: str = 'month',
    slope_scaling: Optional[str] = None,
    x_unit: str = "units",
    continuous_confidence: bool = True,
    **kwargs
) -> pd.DataFrame:
    """
    Calculate rolling Sen's slope over moving time windows.

    Args:
        x: Data vector (array or DataFrame column)
        t: Time vector (array of timestamps or numeric)
        window: Window size.
                - For datetime t: string (e.g., '10Y', '5Y', '365D') or Timedelta-compatible string
                - For numeric t: integer or float (e.g., 10, 5.5)
        step: Step size for sliding the window.
              - For datetime t: string (e.g., '1Y', '6M'). Default is window/2.
              - For numeric t: integer or float. Default is window/2.
        min_size: Minimum number of observations required in a window to calculate a trend.
        alpha: Significance level for the Mann-Kendall test (default 0.05).
        seasonal: If True, uses `seasonal_trend_test` instead of `trend_test`.
        period: The seasonal period (e.g., 12 for monthly data). Used if seasonal=True.
        season_type: The type of seasonality (e.g., 'month'). Used if seasonal=True.
        slope_scaling: Time unit for scaling the Sen's slope (e.g., 'year').
        x_unit: Unit of measurement for x (e.g., 'mg/L').
        continuous_confidence: If True (default for rolling), uses continuous confidence (C)
                               interpretation. If False, uses classical p-value testing.
        **kwargs: Additional arguments passed to `trend_test` or `seasonal_trend_test`.

    Returns:
        pd.DataFrame: A DataFrame where each row corresponds to a time window, containing:
            - window_start, window_end: The time bounds of the window.
            - window_center: The midpoint of the window (useful for plotting).
            - n_obs: Number of observations in the window.
            - slope: The Sen's slope.
            - lower_ci, upper_ci: Confidence intervals for the slope.
            - p_value: The p-value of the trend test.
            - h: Boolean indicating if the trend is significant (at alpha).
            - classification: The trend classification string.
            - C: Confidence in the trend direction.
            - Cd: Directional confidence.
            - tau: Kendall's Tau.
            - s: Mann-Kendall score.
    """
    # Input validation
    x_arr = np.asarray(x) if not isinstance(x, pd.DataFrame) else x
    t_arr = np.asarray(t)

    if len(x_arr) != len(t_arr):
        raise ValueError("x and t must have same length")

    is_datetime = _is_datetime_like(t_arr)

    # Parse window and step
    window_val = None
    step_val = None

    if is_datetime:
        t_series = pd.to_datetime(t_arr)

        # Try parsing as Timedelta first (fixed duration)
        try:
            window_val = pd.Timedelta(window)
        except ValueError:
            # Try parsing as DateOffset (variable duration like 'Y', 'M')
            try:
                window_val = pd.tseries.frequencies.to_offset(window)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid window '{window}' for datetime data. Use a pandas frequency string (e.g., '365D', '10YE').")

        if step:
            try:
                step_val = pd.Timedelta(step)
            except ValueError:
                try:
                    step_val = pd.tseries.frequencies.to_offset(step)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid step '{step}' for datetime data.")
        else:
            # Default step: half window
            # Division is tricky with DateOffsets.
            # If window is offset, we can't easily divide. Default to window (no overlap) or handle specially?
            # Or convert to approximate timedelta for step?
            if isinstance(window_val, pd.Timedelta):
                step_val = window_val / 2
            else:
                # Fallback for Offsets: Just use the offset itself as step (non-overlapping)
                # Or try to construct a half-offset? Not standard.
                # Let's default to window size (no overlap) if we can't divide,
                # OR try to parse roughly.
                # Actually, a safer default for variable offsets is simply 1 of the base unit if possible?
                # No, let's just default to the window itself if we can't divide.
                # Wait, common usage is 10Y window, 1Y step. If step is None, what's sensible?
                # Maybe 1/10th? Or just the window.
                # Let's try to assume step is same as window if we can't divide.
                step_val = window_val

    else:
        t_series = pd.Series(t_arr)
        try:
            window_val = float(window)
        except (ValueError, TypeError):
             raise ValueError(f"Invalid window '{window}' for numeric data. Must be a number.")

        if step:
             try:
                step_val = float(step)
             except (ValueError, TypeError):
                raise ValueError(f"Invalid step '{step}' for numeric data. Must be a number.")
        else:
            step_val = window_val / 2

    # Generate windows
    windows = _generate_windows(t_series, window_val, step_val, is_datetime)

    # Calculate trends for each window
    results = []

    for win_start, win_end in windows:
        # Select data in window [start, end)
        if is_datetime:
            mask = (t_series >= win_start) & (t_series < win_end)
        else:
            mask = (t_series >= win_start) & (t_series < win_end)

        if mask.sum() < min_size:
            continue

        # Extract window data
        if isinstance(x, pd.DataFrame):
            x_window = x[mask].reset_index(drop=True)
        else:
            x_window = x_arr[mask]
        t_window = t_arr[mask]

        # Run trend test
        try:
            common_kwargs = {
                'alpha': alpha,
                'slope_scaling': slope_scaling,
                'x_unit': x_unit,
                'continuous_confidence': continuous_confidence,
                'min_size': None,
                **kwargs
            }

            if seasonal:
                result = seasonal_trend_test(
                    x=x_window,
                    t=t_window,
                    period=period,
                    season_type=season_type,
                    **common_kwargs
                )
            else:
                result = trend_test(
                    x=x_window,
                    t=t_window,
                    **common_kwargs
                )

            # Calculate window center
            if is_datetime:
                # Midpoint calculation
                # If using offsets, win_end - win_start results in a Timedelta usually (if date subtraction)
                # Timestamp - Timestamp = Timedelta
                # So this should work even if created via Offset
                win_center = win_start + (win_end - win_start) / 2
            else:
                win_center = (win_start + win_end) / 2

            results.append({
                'window_start': win_start,
                'window_end': win_end,
                'window_center': win_center,
                'n_obs': int(mask.sum()),
                'slope': result.slope,
                'lower_ci': result.lower_ci,
                'upper_ci': result.upper_ci,
                'p_value': result.p,
                'h': result.h,
                'classification': result.classification,
                'C': result.C,
                'Cd': result.Cd,
                'tau': result.Tau,
                's': result.s
            })

        except Exception as e:
            warnings.warn(f"Failed to calculate trend for window {win_start} to {win_end}: {e}")
            continue

    if not results:
        return pd.DataFrame(columns=[
            'window_start', 'window_end', 'window_center', 'n_obs',
            'slope', 'lower_ci', 'upper_ci', 'p_value', 'h',
            'classification', 'C', 'Cd', 'tau', 's'
        ])

    return pd.DataFrame(results)


def _generate_windows(t_series, window_size, step_size, is_datetime):
    """Generate sliding window boundaries."""
    windows = []

    if len(t_series) == 0:
        return windows

    t_min = t_series.min()
    t_max = t_series.max()

    current = t_min

    while current < t_max:
        # Check if window_size is Timedelta or Offset (or float)
        # Addition works for both Timestamp + Timedelta and Timestamp + DateOffset
        win_end = current + window_size

        windows.append((current, win_end))
        current += step_size

        if len(windows) > 10000:
            raise ValueError("Too many windows generated. Check window/step sizes.")

    return windows


def compare_periods(x, t, breakpoint, alpha=0.05, **kwargs):
    """
    Compare trends before and after a breakpoint.

    Args:
        x: Data vector
        t: Time vector
        breakpoint: Time value to split data (value in t where split occurs)
        alpha: Significance level
        **kwargs: Additional arguments for trend_test

    Returns:
        dict: Dictionary containing:
            - 'before': Result object for pre-breakpoint data
            - 'after': Result object for post-breakpoint data
            - 'slope_difference': slope_after - slope_before
            - 'ci_overlap': Boolean, True if confidence intervals overlap
            - 'significant_change': Boolean, True if CIs do NOT overlap (simple test)
            - 'breakpoint': The breakpoint used
    """
    t_arr = np.asarray(t)
    x_arr = np.asarray(x) if not isinstance(x, pd.DataFrame) else x

    if isinstance(x, pd.DataFrame):
        mask_before = t_arr < breakpoint
        x_before = x[mask_before].reset_index(drop=True)
        x_after = x[~mask_before].reset_index(drop=True)
    else:
        mask_before = t_arr < breakpoint
        x_before = x_arr[mask_before]
        x_after = x_arr[~mask_before]

    t_before = t_arr[mask_before]
    t_after = t_arr[~mask_before]

    if len(t_before) < 3 or len(t_after) < 3:
         warnings.warn("Insufficient data in one or both periods for comparison.")

    result_before = trend_test(x=x_before, t=t_before, alpha=alpha, **kwargs)
    result_after = trend_test(x=x_after, t=t_after, alpha=alpha, **kwargs)

    slope_diff = result_after.slope - result_before.slope

    # Simple overlap test
    # If any CI is NaN, we cannot determine significance
    if np.isnan(result_before.lower_ci) or np.isnan(result_after.lower_ci):
        ci_overlap = np.nan
        significant_change = False
    else:
        no_overlap = (result_before.lower_ci > result_after.upper_ci) or \
                     (result_after.lower_ci > result_before.upper_ci)
        ci_overlap = not no_overlap
        significant_change = no_overlap

    return {
        'before': result_before,
        'after': result_after,
        'slope_difference': slope_diff,
        'ci_overlap': ci_overlap,
        'significant_change': significant_change,
        'breakpoint': breakpoint
    }
