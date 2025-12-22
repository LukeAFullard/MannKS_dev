"""
This script provides a modified version of the Mann-Kendall test
and Sen's slope estimator to handle unequally spaced time series data.
"""
from collections import namedtuple
import numpy as np
import pandas as pd
import warnings
from ._stats import (_z_score, _p_value, _sens_estimator_unequal_spacing,
                     _confidence_intervals, _mk_probability,
                     _mk_score_and_var_censored, _sens_estimator_censored,
                     _sen_probability)
from ._helpers import (_prepare_data, _aggregate_by_group, _value_for_time_increment)
from .plotting import plot_trend
from .analysis_notes import get_analysis_note, get_sens_slope_analysis_note
from .classification import classify_trend


from typing import Union, Tuple, Optional

def trend_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    alpha: float = 0.05,
    hicensor: Union[bool, float] = False,
    plot_path: Optional[str] = None,
    lt_mult: float = 0.5,
    gt_mult: float = 1.1,
    sens_slope_method: str = 'nan',
    tau_method: str = 'b',
    agg_method: str = 'none',
    agg_period: str = 'year',
    min_size: Optional[int] = 10,
    mk_test_method: str = 'robust',
    ci_method: str = 'direct',
    tie_break_method: str = 'robust',
    category_map: Optional[dict] = None,
    x_unit: str = "units",
    slope_scaling: Optional[str] = None
) -> namedtuple:
    """
    Mann-Kendall test for unequally spaced time series.
    Input:
        x: a vector of data, or a DataFrame from prepare_censored_data.
        t: a vector of timestamps corresponding to x.
        alpha: significance level (default 0.05).
        hicensor (bool): If True, applies the high-censor rule, where all
                         values below the highest left-censor limit are
                         treated as censored at that limit.
        plot_path (str, optional): If provided, a plot of the trend analysis
                                   is saved to this file path.
        lt_mult (float): The multiplier for left-censored data, **used only
                         for the Sen's slope calculation** (default 0.5).
                         This does not affect the Mann-Kendall test itself.
        gt_mult (float): The multiplier for right-censored data, **used only
                         for the Sen's slope calculation** (default 1.1).
                         This does not affect the Mann-Kendall test itself.
        sens_slope_method (str): The method for handling ambiguous slopes in censored data.
            - 'nan' (default): Sets ambiguous slopes (e.g., between two left-censored
                               values) to `np.nan`, effectively removing them from the
                               median slope calculation. This is a statistically neutral
                               approach.
            - 'lwp': Sets ambiguous slopes to 0, mimicking the LWP-TRENDS R script.
                     This may bias the slope towards zero and is primarily available
                     for replicating results from that script.
        tau_method (str): The method for calculating Kendall's Tau ('a' or 'b').
                          Default is 'b', which accounts for ties in the data and is
                          the recommended method.
        agg_method (str): The method for aggregating data.
            - **Caution**: Using aggregation with censored data (other than
              'robust_median') is not statistically robust and may produce
              biased results.
            - 'none' (default): No aggregation. A warning is issued if tied
                                timestamps are present.
            - 'lwp': Aggregates data to a single observation per time period defined
                     by `agg_period` (e.g., year, month). This mimics the LWP-TRENDS
                     R script and is useful for handling high-density data
                     clusters. Requires a datetime-like time vector `t`.
            - 'median': Aggregates tied timestamps using the median of values and times.
            - 'robust_median': A more statistically robust median for censored data at
                               tied timestamps.
            - 'middle': Aggregates tied timestamps using the observation closest to the
                        mean of the actual timestamps.
            - 'middle_lwp': Aggregates tied timestamps using the observation closest to the
                            theoretical midpoint of the time period.
        agg_period (str): The time period for LWP aggregation ('year', 'month', etc.).
                          Only used when `agg_method='lwp'`.
        min_size (int): Minimum sample size. Warnings issued if n < min_size.
                       Set to None to disable check.
        mk_test_method (str): The method for handling right-censored data in the
                              Mann-Kendall test.
            - 'robust' (default): A non-parametric approach that handles
              right-censored data without value modification. Recommended for
              most cases.
            - 'lwp': A heuristic from the LWP-TRENDS R script that replaces all
              right-censored values with a value slightly larger than the
              maximum observed right-censored value. Provided for backward
              compatibility.
        ci_method (str): The method for calculating the confidence intervals
                         for the Sen's slope.
            - 'direct' (default): A direct indexing method that rounds the
              ranks to the nearest integer.
            - 'lwp': An interpolation method that mimics the LWP-TRENDS R
              script's `approx` function.
        tie_break_method (str): The method for tie-breaking in the Mann-Kendall test.
            - 'robust' (default): Uses a small epsilon based on half the minimum
              difference between unique values. Robust and recommended.
            - 'lwp': Divides the minimum difference by 1000 to closely replicate
              the behavior of the LWP-TRENDS R script. Use for compatibility.
        x_unit (str): A string representing the units of the data vector `x`.
                      This is used to create an informative `slope_units` string in the output.
        slope_scaling (str, optional): The time unit to which the Sen's slope should be scaled.
                                       For example, if `slope_scaling='year'`, the slope will be
                                       converted to units per year. This only applies when using
                                       a datetime-like time vector `t`.
    Output:
        A namedtuple containing the following fields:
        - trend: The trend of the data ('increasing', 'decreasing', or 'no trend').
        - h: A boolean indicating whether the trend is significant.
        - p: The p-value of the test.
        - z: The Z-statistic.
        - Tau: Kendall's Tau, a measure of correlation between the data and time.
               Ranges from -1 (perfectly decreasing) to +1 (perfectly increasing).
        - s: The Mann-Kendall score.
        - var_s: The variance of `s`.
        - slope: The Sen's slope.
        - intercept: The intercept of the trend line.
        - lower_ci: The lower confidence interval of the slope.
        - upper_ci: The upper confidence interval of the slope.
        - C: The confidence of the trend direction.
        - Cd: The confidence that the trend is decreasing.

    Statistical Assumptions:
    ----------------------
    The Mann-Kendall test and Sen's slope estimator are non-parametric methods
    and do not require data to be normally distributed. However, they rely on
    the following assumptions:

    1.  **Independence**: The data points are serially independent. The presence
        of autocorrelation (serial correlation) can violate this assumption and
        affect the significance of the results.

        **Autocorrelation Warning:**
        This test assumes independent observations. If your data has significant
        autocorrelation (serial correlation), the test may show spurious
        significance. For environmental time series, consider pre-whitening or
        block bootstrap methods if autocorrelation is present.
    2.  **Monotonic Trend**: The trend is assumed to be monotonic, meaning it is
        consistently in one direction (either increasing or decreasing) over
        the time period. The test is not suitable for detecting non-monotonic
        (e.g., cyclical) trends.
    3.  **Homogeneity of Variance**: While not strictly required, the test is
        most powerful when the variance of the data is homogeneous over time.
    4.  **Continuous Data**: The test is designed for continuous data. Although it
        can handle ties, a large number of ties can reduce its power.
    5.  **Normal Approximation**: For sample sizes typically > 10, the test
        statistic `S` is assumed to be approximately normally distributed, which
        is used to calculate the Z-score and p-value. This approximation may be
        less accurate for very small sample sizes with many ties.
    6.  **Linear Trend (for Sen's Slope)**: Sen's slope provides a linear estimate
        of the trend, and the confidence intervals are based on this assumption.
    """
    # --- Basic Input Validation ---
    x_arr = np.asarray(x) if not isinstance(x, pd.DataFrame) else x
    t_arr = np.asarray(t)
    if len(x_arr) != len(t_arr):
        raise ValueError(f"Input vectors `x` and `t` must have the same length. Got {len(x_arr)} and {len(t_arr)}.")
    if not 0 < alpha < 1:
        raise ValueError(f"Significance level `alpha` must be between 0 and 1. Got {alpha}.")

    res = namedtuple('Mann_Kendall_Test', [
        'trend', 'h', 'p', 'z', 'Tau', 's', 'var_s', 'slope', 'intercept',
        'lower_ci', 'upper_ci', 'C', 'Cd', 'classification', 'analysis_notes',
        'sen_probability', 'sen_probability_max', 'sen_probability_min',
        'prop_censored', 'prop_unique', 'n_censor_levels',
        'slope_per_second', 'lower_ci_per_second', 'upper_ci_per_second',
        'scaled_slope', 'slope_units'
    ])

    # --- Method String Validation ---
    valid_sens_slope_methods = ['nan', 'lwp']
    if sens_slope_method not in valid_sens_slope_methods:
        raise ValueError(f"Invalid `sens_slope_method`. Must be one of {valid_sens_slope_methods}.")

    valid_tau_methods = ['a', 'b']
    if tau_method not in valid_tau_methods:
        raise ValueError(f"Invalid `tau_method`. Must be one of {valid_tau_methods}.")

    valid_agg_methods = ['none', 'median', 'robust_median', 'middle', 'middle_lwp', 'lwp']
    if agg_method not in valid_agg_methods:
        raise ValueError(f"Invalid `agg_method`. Must be one of {valid_agg_methods}.")

    valid_mk_test_methods = ['robust', 'lwp']
    if mk_test_method not in valid_mk_test_methods:
        raise ValueError(f"Invalid `mk_test_method`. Must be one of {valid_mk_test_methods}.")

    valid_ci_methods = ['direct', 'lwp']
    if ci_method not in valid_ci_methods:
        raise ValueError(f"Invalid `ci_method`. Must be one of {valid_ci_methods}.")

    valid_tie_break_methods = ['robust', 'lwp']
    if tie_break_method not in valid_tie_break_methods:
        raise ValueError(f"Invalid `tie_break_method`. Must be one of {valid_tie_break_methods}.")

    analysis_notes = []
    data_filtered, is_datetime = _prepare_data(x, t, hicensor)

    note = get_analysis_note(data_filtered, values_col='value', censored_col='censored')
    analysis_notes.append(note)

    n = len(data_filtered)

    # Sample size validation
    if n < 2:
        return res('no trend', False, np.nan, 0, 0, 0, 0, np.nan, np.nan,
                   np.nan, np.nan, np.nan, np.nan, 'insufficient data', analysis_notes,
                   np.nan, np.nan, np.nan, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, '')

    if min_size is not None and n < min_size:
        analysis_notes.append(f'sample size ({n}) below minimum ({min_size})')


    # Handle tied timestamps and temporal aggregation
    if agg_method == 'lwp':
        if not is_datetime:
            raise ValueError("`agg_method='lwp'` can only be used with datetime-like inputs for `t`.")
        # LWP aggregation selects one value per time period (e.g., year, month).
        data_filtered = _value_for_time_increment(data_filtered, is_datetime=True, season_type=agg_period)
    elif len(data_filtered['t']) != len(np.unique(data_filtered['t'])):
        if agg_method == 'none':
            analysis_notes.append('tied timestamps present without aggregation')
        else:
            # Standard aggregation for tied timestamps.
            if data_filtered['censored'].any() and agg_method not in ['robust_median']:
                analysis_notes.append(f"'{agg_method}' aggregation used with censored data")

            agg_data_list = [
                _aggregate_by_group(group, agg_method, is_datetime)
                for _, group in data_filtered.groupby('t')
            ]
            data_filtered = pd.concat(agg_data_list, ignore_index=True)

    x_filtered = data_filtered['value'].to_numpy()
    t_filtered = data_filtered['t'].to_numpy()
    censored_filtered = data_filtered['censored'].to_numpy()
    cen_type_filtered = data_filtered['cen_type'].to_numpy()

    note = get_analysis_note(data_filtered, values_col='value', censored_col='censored', post_aggregation=True)
    analysis_notes.append(note)


    if len(x_filtered) < 2:
        return res('no trend', False, np.nan, 0, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,
                   'insufficient data post-aggregation', analysis_notes,
                   np.nan, np.nan, np.nan, 0, 0, 0, np.nan, np.nan, np.nan, np.nan, '')

    s, var_s, D, Tau = _mk_score_and_var_censored(
        x_filtered, t_filtered, censored_filtered, cen_type_filtered,
        tau_method=tau_method, mk_test_method=mk_test_method,
        tie_break_method=tie_break_method
    )

    z = _z_score(s, var_s)
    p, h, trend = _p_value(z, alpha)
    C, Cd = _mk_probability(p, s)

    if np.any(censored_filtered):
        slopes = _sens_estimator_censored(
            x_filtered, t_filtered, cen_type_filtered,
            lt_mult=lt_mult, gt_mult=gt_mult, method=sens_slope_method
        )
    else:
        slopes = _sens_estimator_unequal_spacing(x_filtered, t_filtered)

    slope = np.nanmedian(slopes) if len(slopes) > 0 else np.nan

    note = get_sens_slope_analysis_note(slopes, t_filtered, cen_type_filtered)
    analysis_notes.append(note)


    if np.isnan(slope):
        intercept = np.nan
    else:
        intercept = np.nanmedian(x_filtered) - np.nanmedian(t_filtered) * slope

    lower_ci, upper_ci = _confidence_intervals(slopes, var_s, alpha, method=ci_method)

    # Sen's slope probability
    sen_prob, sen_prob_max, sen_prob_min = _sen_probability(slopes, var_s)

    # --- Slope Scaling ---
    slope_per_second = slope
    scaled_slope = slope
    slope_units = ""
    scaled_lower_ci = lower_ci
    scaled_upper_ci = upper_ci

    if slope_scaling and pd.notna(slope):
        if is_datetime:
            from ._helpers import _get_slope_scaling_factor
            try:
                factor = _get_slope_scaling_factor(slope_scaling)
                scaled_slope = slope * factor
                scaled_lower_ci = lower_ci * factor
                scaled_upper_ci = upper_ci * factor
                slope_units = f"{x_unit} per {slope_scaling.lower()}"
            except (ValueError, TypeError) as e:
                warnings.warn(f"Slope scaling failed: {e}", UserWarning)
                slope_units = f"{x_unit} per second" # Fallback
        else:
            warnings.warn(
                "Cannot apply `slope_scaling` to a numeric (non-datetime) "
                "time vector `t`. The slope's unit is inherited from `t`.",
                UserWarning
            )
            slope_units = f"{x_unit} per unit of t" # Clarify for numeric time
    elif is_datetime:
        slope_units = f"{x_unit} per second"
    else: # Numeric time without scaling
        slope_units = f"{x_unit} per unit of t"


    # Calculate metadata fields
    prop_censored = np.sum(censored_filtered) / n if n > 0 else 0
    prop_unique = len(np.unique(x_filtered)) / n if n > 0 else 0
    n_censor_levels = len(np.unique(x_filtered[censored_filtered])) if np.sum(censored_filtered) > 0 else 0

    results = res(trend, h, p, z, Tau, s, var_s, scaled_slope, intercept, scaled_lower_ci, scaled_upper_ci, C, Cd,
                  '', [], sen_prob, sen_prob_max, sen_prob_min,
                  prop_censored, prop_unique, n_censor_levels,
                  slope_per_second, lower_ci, upper_ci,
                  scaled_slope, slope_units)


    # Final Classification and Notes
    classification = classify_trend(results, category_map=category_map)
    final_notes = [note for note in analysis_notes if note != 'ok']

    final_results = results._replace(classification=classification, analysis_notes=final_notes)

    if plot_path:
        plot_trend(data_filtered, final_results, plot_path, alpha)

    return final_results
