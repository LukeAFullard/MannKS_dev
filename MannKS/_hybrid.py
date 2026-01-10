
import numpy as np
import piecewise_regression
import warnings
from ._stats import (
    _sens_estimator_unequal_spacing,
    _sens_estimator_censored,
    _mk_score_and_var_censored,
    _confidence_intervals
)

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

                    if bic < best_bic:
                        best_bic = bic
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
                    if hasattr(pw_fit, 'best_muggeo') and hasattr(pw_fit.best_muggeo, 'best_fit'):
                        bf = pw_fit.best_muggeo.best_fit
                        if hasattr(bf, 'bic'):
                            current_bic = bf.bic
                    else:
                        res = pw_fit.get_results()
                        current_bic = res.get('bic', np.inf)

                    if current_bic < best_bic:
                        best_bic = current_bic
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
