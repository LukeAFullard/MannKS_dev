
import numpy as np
import piecewise_regression
from scipy.stats import gaussian_kde
from scipy.signal import find_peaks
import warnings

def _bootstrap_breakpoints(t, x, n_breakpoints, n_bootstrap=100, alpha_n=0.05):
    """
    Bootstrap the breakpoint detection to find robust breakpoint locations.

    Args:
        t: Time vector
        x: Data vector
        n_breakpoints: Number of breakpoints to find
        n_bootstrap: Number of bootstrap iterations
        alpha_n: Significance level (not used directly here but standard arg)

    Returns:
        all_breakpoints: Flat list of all breakpoints found across bootstraps
    """
    # Explicit conversion to numpy arrays for safety
    t = np.asarray(t)
    x = np.asarray(x)

    n = len(x)
    all_breakpoints = []

    for _ in range(n_bootstrap):
        # Bootstrap Resampling
        indices = np.random.choice(n, n, replace=True)
        t_boot = t[indices]
        x_boot = x[indices]

        # Sort for piecewise_regression
        sort_idx = np.argsort(t_boot)
        t_boot = t_boot[sort_idx]
        x_boot = x_boot[sort_idx]

        try:
            # We fix the number of breakpoints to what was requested/estimated
            pw_fit = piecewise_regression.Fit(t_boot, x_boot, n_breakpoints=n_breakpoints, verbose=False)

            # Extract estimates
            estimates = None
            if hasattr(pw_fit, 'best_muggeo') and hasattr(pw_fit.best_muggeo, 'best_fit'):
                 estimates = pw_fit.best_muggeo.best_fit.estimates
            elif hasattr(pw_fit, 'get_results'):
                 estimates = pw_fit.get_results().get('estimates')

            if estimates:
                for key, val in estimates.items():
                    if key.startswith('breakpoint'):
                        all_breakpoints.append(val['estimate'])
        except:
            continue

    return np.array(all_breakpoints)

def find_bagged_breakpoints(t, x, n_breakpoints, n_bootstrap=100):
    """
    Find robust breakpoints using Bagging and KDE.

    1. Bootstrap data and find breakpoints.
    2. Use KDE to estimate the density of breakpoints.
    3. Find peaks in the density to identify robust locations.

    Args:
        t: Time vector
        x: Data vector
        n_breakpoints: Number of breakpoints to identify
        n_bootstrap: Number of bootstrap iterations

    Returns:
        robust_breakpoints: Array of robust breakpoint locations
    """
    # Explicit conversion to numpy arrays for safety
    t = np.asarray(t)
    x = np.asarray(x)

    if n_breakpoints == 0:
        return np.array([])

    all_bps = _bootstrap_breakpoints(t, x, n_breakpoints, n_bootstrap)

    if len(all_bps) == 0:
        warnings.warn("Bagging failed to find any breakpoints.")
        return np.array([])

    # KDE
    try:
        kde = gaussian_kde(all_bps)

        # Grid for evaluating KDE
        t_grid = np.linspace(t.min(), t.max(), 500)
        density = kde(t_grid)

        # Find peaks
        peaks, _ = find_peaks(density)

        if len(peaks) == 0:
            return np.array([])

        # Sort peaks by density height
        peak_heights = density[peaks]
        sorted_peak_indices = np.argsort(peak_heights)[::-1] # Descending

        # Select top n_breakpoints
        top_peaks = peaks[sorted_peak_indices[:n_breakpoints]]
        robust_bps = t_grid[top_peaks]

        return np.sort(robust_bps)

    except Exception as e:
        warnings.warn(f"KDE estimation failed: {e}")
        return np.array([])
