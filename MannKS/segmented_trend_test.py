
import numpy as np
import pandas as pd
import piecewise_regression
import warnings
from collections import namedtuple
from typing import Union, Optional, List, Tuple
from scipy.stats import norm

from ._stats import (
    _sens_estimator_unequal_spacing,
    _sens_estimator_censored,
    _mk_score_and_var_censored,
    _confidence_intervals
)
from .trend_test import trend_test
from ._datetime import _to_numeric_time, _is_datetime_like

class HybridSegmentedTrend:
    """
    Hybrid Segmented Regression.

    Phase 1 (Structure Discovery): Uses OLS (piecewise-regression) to find
    the number and location of breakpoints.

    Phase 2 (Robust Estimation): Uses Mann-Kendall / Sen's Slope on the
    identified segments to estimate robust slopes and confidence intervals.
    """

    def __init__(self, max_breakpoints=5, n_breakpoints=None):
        """
        Args:
            max_breakpoints (int): Maximum number of breakpoints to search for (if n_breakpoints is None).
            n_breakpoints (int, optional): Fixed number of breakpoints to fit.
        """
        self.max_breakpoints = max_breakpoints
        self.n_breakpoints = n_breakpoints

        self.breakpoints_ = None
        self.segments_ = None
        self.n_breakpoints_ = None
        self.bic_ = None
        self.aic_ = None

    def fit(self, t, x, censored=None, cen_type=None, lt_mult=0.5, gt_mult=1.1):
        t = np.asarray(t)
        x = np.asarray(x)

        # Sort data
        sort_idx = np.argsort(t)
        t = t[sort_idx]
        x = x[sort_idx]

        if censored is not None:
            censored = np.asarray(censored)[sort_idx]
            cen_type = np.asarray(cen_type)[sort_idx]
            # OLS needs numeric x. Substitute censored values.
            x_ols = x.copy().astype(float)
            x_ols[cen_type == 'lt'] *= lt_mult
            x_ols[cen_type == 'gt'] *= gt_mult
        else:
            x_ols = x

        # --- Phase 1: Structure Discovery (OLS) ---

        best_n = 0
        best_bps = []
        best_bic = np.inf
        best_aic = np.inf

        n_range = []
        if self.n_breakpoints is not None:
            n_range = [self.n_breakpoints]
        else:
            n_range = range(self.max_breakpoints + 1)

        for k in n_range:
            if k == 0:
                # Linear Fit BIC
                # RSS = sum((y - (a+bt))^2)
                try:
                    p = np.polyfit(t, x_ols, 1)
                    y_pred = np.polyval(p, t)
                    rss = np.sum((x_ols - y_pred)**2)
                    n_samples = len(x)
                    if rss <= 1e-10: rss = 1e-10
                    # k_params = 2 (slope, intercept)
                    bic = n_samples * np.log(rss/n_samples) + 2 * np.log(n_samples)
                    aic = n_samples * np.log(rss/n_samples) + 2 * 2

                    if bic < best_bic:
                        best_bic = bic
                        best_aic = aic
                        best_n = 0
                        best_bps = []
                except:
                    pass
            else:
                try:
                    pw_fit = piecewise_regression.Fit(t, x_ols, n_breakpoints=k, verbose=False)
                    # Check BIC
                    # Access library BIC safely
                    current_bic = np.inf
                    current_aic = np.inf

                    # Try accessing BIC from library structure
                    if hasattr(pw_fit, 'best_muggeo') and hasattr(pw_fit.best_muggeo, 'best_fit'):
                        bf = pw_fit.best_muggeo.best_fit
                        if hasattr(bf, 'bic'):
                            current_bic = bf.bic
                            # Estimate AIC if not present
                            # BIC = n*ln(RSS/n) + k*ln(n)
                            # AIC = n*ln(RSS/n) + 2*k
                            # AIC = BIC - k*ln(n) + 2*k
                            k_params = 2 * k + 2
                            n_samples = len(x)
                            current_aic = current_bic - k_params * np.log(n_samples) + 2 * k_params
                    else:
                        res = pw_fit.get_results()
                        current_bic = res.get('bic', np.inf)
                        # Try to get AIC or estimate
                        current_aic = current_bic # Fallback if calculation complex

                    if current_bic < best_bic:
                        best_bic = current_bic
                        best_aic = current_aic
                        best_n = k

                        # Extract BPs
                        estimates = None
                        if hasattr(pw_fit, 'best_muggeo') and hasattr(pw_fit.best_muggeo, 'best_fit'):
                             estimates = pw_fit.best_muggeo.best_fit.estimates
                        elif hasattr(pw_fit, 'get_results'):
                             estimates = pw_fit.get_results().get('estimates')

                        bps = []
                        if estimates:
                            for key, val in estimates.items():
                                if key.startswith('breakpoint'):
                                    bps.append(val['estimate'])
                        best_bps = sorted(bps)
                except:
                    continue

        self.n_breakpoints_ = best_n
        self.breakpoints_ = np.array(best_bps)
        self.bic_ = best_bic
        self.aic_ = best_aic

        # --- Phase 2: Robust Estimation (MannKS) ---

        self.segments_ = []
        boundaries = np.concatenate(([t.min()], self.breakpoints_, [t.max()]))

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
                self.segments_.append({
                    'slope': np.nan, 'intercept': np.nan,
                    'lower_ci': np.nan, 'upper_ci': np.nan,
                    'n': 0
                })
                continue

            if censored is not None:
                cen_seg = censored[mask]
                cen_type_seg = cen_type[mask]
                slopes = _sens_estimator_censored(x_seg, t_seg, cen_type_seg, lt_mult, gt_mult)
                # We also need s and var_s for CIs
                s, var_s, _, _ = _mk_score_and_var_censored(x_seg, t_seg, cen_seg, cen_type_seg)
            else:
                slopes = _sens_estimator_unequal_spacing(x_seg, t_seg)
                dummy_cen = np.zeros(len(x_seg), dtype=bool)
                dummy_type = np.full(len(x_seg), 'not', dtype=object)
                s, var_s, _, _ = _mk_score_and_var_censored(x_seg, t_seg, dummy_cen, dummy_type)

            slope = np.nanmedian(slopes)
            lower_ci, upper_ci = _confidence_intervals(slopes, var_s, alpha=0.05)

            # Robust Intercept
            if censored is not None:
                uncensored_mask = ~cen_seg.astype(bool)
                if np.any(uncensored_mask):
                    intercept = np.median(x_seg[uncensored_mask] - slope * t_seg[uncensored_mask])
                else:
                    intercept = np.nan
            else:
                intercept = np.median(x_seg - slope * t_seg)

            self.segments_.append({
                'slope': slope,
                'intercept': intercept,
                'lower_ci': lower_ci,
                'upper_ci': upper_ci,
                'n': len(x_seg)
            })

    def predict(self, t):
        t = np.asarray(t)
        y_pred = np.zeros_like(t, dtype=float)
        y_pred[:] = np.nan

        if self.segments_ is None or len(self.segments_) == 0:
            return y_pred

        bps = self.breakpoints_
        if len(bps) == 0:
             seg = self.segments_[0]
             return seg['slope'] * t + seg['intercept']

        mask = t < bps[0]
        seg = self.segments_[0]
        y_pred[mask] = seg['slope'] * t[mask] + seg['intercept']

        for i in range(len(bps) - 1):
            mask = (t >= bps[i]) & (t < bps[i+1])
            seg = self.segments_[i+1]
            y_pred[mask] = seg['slope'] * t[mask] + seg['intercept']

        mask = t >= bps[-1]
        seg = self.segments_[-1]
        y_pred[mask] = seg['slope'] * t[mask] + seg['intercept']

        return y_pred

def _prepare_data(x, t, hicensor=False):
    """
    Internal helper to prepare data for segmented analysis.
    """
    is_dt = _is_datetime_like(t)
    t_num = _to_numeric_time(t)

    if isinstance(x, pd.DataFrame):
        df = x.copy()
        if 'value' not in df.columns:
             if x.shape[1] == 1:
                 df.columns = ['value']
                 df['censored'] = False
                 df['cen_type'] = 'none'
             else:
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

    df = df.sort_values('t').reset_index(drop=True)

    if hicensor:
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
    n_breakpoints: Optional[int] = None, # None means search up to max
    max_breakpoints: int = 5,
    alpha: float = 0.05,
    hicensor: Union[bool, float] = False,
    criterion: str = 'bic', # Only BIC supported by Hybrid really, but keeps API
    **kwargs
):
    """
    Perform Hybrid Segmented Trend Analysis.

    This function is a wrapper around `HybridSegmentedTrend`. It combines:
    1. OLS-based breakpoint detection (Piecewise Regression).
    2. Robust Mann-Kendall / Sen's slope estimation on the identified segments.

    Args:
        x: Data vector or DataFrame.
        t: Time vector.
        n_breakpoints: Fixed number of breakpoints. If None, optimal number is searched.
        max_breakpoints: Maximum number of breakpoints to search (if n_breakpoints is None).
        alpha: Significance level for confidence intervals.
        hicensor: High-censor rule flag.
        criterion: 'bic' is used for model selection.
        **kwargs: Additional arguments for trend estimation (e.g. lt_mult, gt_mult).

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

    # 2. Fit Hybrid Model
    hybrid_model = HybridSegmentedTrend(max_breakpoints=max_breakpoints, n_breakpoints=n_breakpoints)

    # Extract kwargs relevant for estimation
    lt_mult = kwargs.get('lt_mult', 0.5)
    gt_mult = kwargs.get('gt_mult', 1.1)

    hybrid_model.fit(t_numeric, x_val, censored, cen_type, lt_mult, gt_mult)

    # 3. Format Results
    breakpoints = hybrid_model.breakpoints_
    n_bp = hybrid_model.n_breakpoints_

    # Convert breakpoints back to original time format if datetime
    if is_datetime:
        breakpoints_final = pd.to_datetime(breakpoints, unit='s')
    else:
        breakpoints_final = breakpoints

    # Breakpoint CIs are not natively provided by the simple Hybrid fit (OLS SEs exist but not exposed here easily yet)
    # We return NaNs for now or implement bootstrap if requested.
    # For now, to match "clean" request, we keep it simple.
    breakpoint_cis = [(np.nan, np.nan)] * n_bp

    # Format segments for output
    segments_list = hybrid_model.segments_
    # We want to maybe add 'p_value' or 'significance' to segments?
    # Mann-Kendall test in Phase 2 calculated 's' and 'var_s'.
    # We could calculate p-values. But `_confidence_intervals` was used.
    # Let's keep it consistent with simple output.

    Result = namedtuple('Segmented_Trend_Test', [
        'n_breakpoints', 'breakpoints', 'breakpoint_cis', 'segments',
        'is_datetime', 'bic', 'aic', 'score'
    ])

    return Result(
        n_breakpoints=n_bp,
        breakpoints=breakpoints_final,
        breakpoint_cis=breakpoint_cis,
        segments=pd.DataFrame(segments_list),
        is_datetime=is_datetime,
        bic=hybrid_model.bic_,
        aic=hybrid_model.aic_,
        score=hybrid_model.bic_ # Default score
    )
