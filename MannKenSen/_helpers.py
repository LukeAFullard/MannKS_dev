import datetime
import numpy as np
import pandas as pd
from ._datetime import _is_datetime_like


def _preprocessing(x):
    x = np.asarray(x)

    # Convert datetime objects to numeric timestamps if necessary
    if _is_datetime_like(x):
        x = x.astype('datetime64[s]').astype(float)
    elif x.dtype == 'O' and len(x) > 0:
        if isinstance(x[0], datetime.datetime):
            x = np.array([val.timestamp() for val in x])

    x = x.astype(float)

    if x.ndim == 2:
        (n, c) = x.shape
        if c == 1:
            x = x.flatten()
    return x, (1 if x.ndim == 1 else x.shape[1])

def _missing_values_analysis(x, method='skip'):
    if method.lower() == 'skip':
        if x.ndim == 1:
            x = x[~np.isnan(x)]
        else:
            x = x[~np.isnan(x).any(axis=1)]
    return x, len(x)


def _aggregate_censored_median(group, is_datetime):
    """
    Computes a robust median for a group of observations which may contain
    censored data, following the LWP-TRENDS R script logic.

    .. note::
        The logic for determining if the aggregated median is censored
        (i.e., `median_val <= max_censored_value`) is a heuristic method.
        It is designed to replicate the behavior of the LWP-TRENDS R script
        and may not be statistically robust in all scenarios.
    """
    n = len(group)
    if n == 0:
        return pd.DataFrame({
            'value': [], 'censored': [], 'cen_type': [],
            't_original': [], 't': []
        })

    # Compute median value
    median_val = group['value'].median()

    # Determine if median is censored (R logic)
    if not group['censored'].any():
        is_censored = False
        cen_type = 'not'
    else:
        # Get maximum censored value
        max_censored = group.loc[group['censored'], 'value'].max()
        is_censored = median_val <= max_censored

        if is_censored:
            # Safely get the most common censor type
            cen_type_mode = group.loc[group['censored'], 'cen_type'].mode()
            if len(cen_type_mode) == 0:
                # All censored values are NaN, default to 'not'
                cen_type = 'not'
                is_censored = False
            else:
                cen_type = cen_type_mode.iloc[0]
        else:
            cen_type = 'not'

    row_data = {
        'value': median_val,
        'censored': is_censored,
        'cen_type': cen_type,
    }

    # Always aggregate time using the median of the original timestamps
    row_data['t_original'] = group['t_original'].median() if is_datetime else np.median(group['t_original'])
    row_data['t'] = np.median(group['t'])

    return pd.DataFrame([row_data])


def _prepare_data(x, t, hicensor):
    """
    Internal helper to prepare and validate data for trend tests.
    """
    if isinstance(x, pd.DataFrame) and all(col in x.columns for col in ['value', 'censored', 'cen_type']):
        data = x.copy()
    elif hasattr(x, '__iter__') and any(isinstance(i, str) for i in x):
        raise TypeError("Input data `x` contains strings. Please pre-process it with `prepare_censored_data` first.")
    else:
        x_proc, _ = _preprocessing(x)
        data = pd.DataFrame({
            'value': x_proc,
            'censored': np.zeros(len(x_proc), dtype=bool),
            'cen_type': np.full(len(x_proc), 'not', dtype=object)
        })

    t_raw = np.asarray(t)
    is_datetime = _is_datetime_like(t_raw)
    t_numeric, _ = _preprocessing(t_raw)
    data['t_original'] = t_raw
    data['t'] = t_numeric

    # Handle missing values
    mask = ~np.isnan(data['value'])
    data_filtered = data[mask].copy()

    # Apply HiCensor rule if requested
    if hicensor and 'lt' in data_filtered['cen_type'].values:
        max_lt_censor = data_filtered.loc[data_filtered['cen_type'] == 'lt', 'value'].max()
        hi_censor_mask = data_filtered['value'] < max_lt_censor
        data_filtered.loc[hi_censor_mask, 'censored'] = True
        data_filtered.loc[hi_censor_mask, 'cen_type'] = 'lt'
        data_filtered.loc[hi_censor_mask, 'value'] = max_lt_censor

    return data_filtered, is_datetime


def _aggregate_by_group(group, agg_method, is_datetime):
    """
    Aggregates a group of data points using the specified method.
    """
    if len(group) <= 1:
        return group

    if agg_method == 'median':
        if group['censored'].any():
            import warnings
            warnings.warn(
                "The 'median' aggregation method uses a simple heuristic for censored data, "
                "which may not be statistically robust. Consider using 'robust_median' for "
                "more accurate censored data aggregation.", UserWarning)
        median_val = group['value'].median()
        is_censored = median_val <= group[group['censored']]['value'].max() if group['censored'].any() else False

        new_row = {
            'value': median_val,
            't_original': group['t_original'].median() if is_datetime else np.median(group['t_original']),
            't': np.median(group['t']),
            'censored': is_censored,
            'cen_type': group.loc[group['censored'], 'cen_type'].mode()[0] if is_censored else 'not'
        }
        return pd.DataFrame([new_row])
    elif agg_method == 'robust_median':
        return _aggregate_censored_median(group, is_datetime)
    elif agg_method == 'middle':
        t_numeric_group = group['t'].to_numpy()
        closest_idx = np.argmin(np.abs(t_numeric_group - np.mean(t_numeric_group)))
        return group.iloc[[closest_idx]]
    return group
