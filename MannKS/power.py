"""
Power analysis for surrogate data testing.

This module provides tools to estimate the statistical power of the surrogate trend test
against colored noise backgrounds via Monte Carlo simulation.
"""

import numpy as np
import pandas as pd
import warnings
from typing import Union, Optional, List, NamedTuple, Dict
from scipy.interpolate import interp1d

from ._surrogate import surrogate_test, _iaaft_surrogates, _lomb_scargle_surrogates, HAS_ASTROPY
from ._helpers import _preprocessing

class PowerResult(NamedTuple):
    """Container for power analysis results."""
    slopes: np.ndarray
    power: np.ndarray
    min_detectable_trend: float
    n_simulations: int
    n_surrogates_inner: int
    alpha: float
    simulation_results: pd.DataFrame
    noise_method: str

def power_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    slopes: Union[List[float], np.ndarray],
    n_simulations: int = 100,
    n_surrogates: int = 1000,
    alpha: float = 0.05,
    surrogate_method: str = 'auto',
    random_state: Optional[int] = None,
    surrogate_kwargs: Optional[dict] = None,
    **kwargs
) -> PowerResult:
    """
    Estimates the statistical power of the surrogate trend test via Monte Carlo simulation.

    Generates synthetic datasets by injecting deterministic trends into colored noise
    realizations (derived from the input data's spectral properties) and calculating
    the frequency of significant detections.

    Args:
        x (Union[np.ndarray, pd.DataFrame]): Input data (used to define the noise model).
        t (np.ndarray): Time values.
        slopes (Union[List[float], np.ndarray]): List of trend slopes (beta) to test.
        n_simulations (int): Number of Monte Carlo simulations per slope.
        n_surrogates (int): Number of surrogates used in the *inner* significance test.
        alpha (float): Significance level for detection (default 0.05).
        surrogate_method (str): Method for surrogate generation ('auto', 'iaaft', 'lomb_scargle').
            Used for both noise generation and the inner test.
        random_state (Optional[int]): Seed for reproducibility.
        surrogate_kwargs (dict, optional): Additional arguments passed to the surrogate generator
            (e.g., {'dy': errors, 'freq_method': 'log'}).
        **kwargs: Additional arguments passed to `surrogate_test`.

    Returns:
        PowerResult: Named tuple containing power curve, MDT, and details.
    """
    x_arr = np.asarray(x).flatten()
    t_arr = np.asarray(t).flatten()
    # Convert t to numeric (float seconds if datetime) using internal helper
    t_numeric, _ = _preprocessing(t_arr)

    slopes_arr = np.asarray(slopes)

    # Validation
    if len(x_arr) != len(t_numeric):
        raise ValueError("x and t must have the same length.")

    surr_kwargs = surrogate_kwargs.copy() if surrogate_kwargs else {}

    # 1. Determine Method and Generate Base Noise Model
    # We generate 'n_simulations' *independent* noise realizations.
    # These represent the "Null" world (no deterministic trend, just colored noise).

    rng = np.random.default_rng(random_state)

    # Check method
    is_uniform = np.allclose(np.diff(t_numeric), np.diff(t_numeric)[0], rtol=1e-3)

    if surrogate_method == 'auto':
        if is_uniform:
            method_used = 'iaaft'
        else:
            if HAS_ASTROPY:
                method_used = 'lomb_scargle'
            else:
                warnings.warn("Uneven sampling but astropy not found. Fallback to IAAFT.", UserWarning)
                method_used = 'iaaft'
    else:
        method_used = surrogate_method

    # Generate the noise bank
    # We use the internal generators directly to get the batch of noise
    # Note: These functions return (n_surrogates, n_samples)

    # Extract specific kwargs for the generator
    gen_kwargs = surr_kwargs.copy()

    if method_used == 'lomb_scargle':
        if not HAS_ASTROPY:
            raise ImportError("Method 'lomb_scargle' requires `astropy`.")

        noise_bank = _lomb_scargle_surrogates(
            x_arr, t_numeric,
            n_surrogates=n_simulations,
            random_state=random_state,
            **gen_kwargs
        )
    elif method_used == 'iaaft':
        noise_bank = _iaaft_surrogates(
            x_arr,
            n_surrogates=n_simulations,
            random_state=random_state,
            # IAAFT accepts max_iter, tol in kwargs? No, explicit args.
            # We map from surr_kwargs if present
            max_iter=gen_kwargs.get('max_iter', 100),
            tol=gen_kwargs.get('tol', 1e-6)
        )
    else:
        raise ValueError(f"Unknown method '{method_used}'")

    # 2. Monte Carlo Loop

    results = []

    # Center time for trend injection to avoid huge intercepts
    t_centered = t_numeric - np.mean(t_numeric)

    power_values = []

    for beta in slopes_arr:
        n_detected = 0

        # We assume the noise_bank has shape (n_simulations, n_samples)
        # For each realization...
        for i in range(n_simulations):
            noise = noise_bank[i]

            # Inject Trend
            x_sim = noise + beta * t_centered

            # Run Test
            # We must use a DIFFERENT random state for the test to avoid correlation
            # with the generation (though likelihood is low).
            # Or just let it be random (None).

            # Note: We pass surrogate_kwargs to the test as well
            # The test will generate `n_surrogates` internal surrogates

            # We suppress warnings to avoid flooding stdout with "Censored data..." or perf warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                res = surrogate_test(
                    x_sim, t_numeric,
                    method=method_used,
                    n_surrogates=n_surrogates,
                    # surrogate_test does not take alpha as argument
                    random_state=None, # Let it be random
                    **surr_kwargs
                )

            # Check detection
            if res.p_value < alpha:
                n_detected += 1

        power = n_detected / n_simulations
        power_values.append(power)

        results.append({
            'slope': beta,
            'power': power,
            'n_detected': n_detected,
            'n_simulations': n_simulations
        })

    power_arr = np.array(power_values)

    # 3. Calculate Minimum Detectable Trend (MDT) at 80% Power
    # We use linear interpolation looking for the 0.8 crossing.

    mdt = np.nan
    target_power = 0.8

    # Check if we crossed 0.8
    # We assume monotonic increase. If not, this is approximate.
    if np.min(power_arr) < target_power and np.max(power_arr) >= target_power:
        try:
            # We can only interpolate strictly monotonic segments.
            # Let's just fit the whole curve if monotonic-ish,
            # or find the first crossing.

            # Find index where power >= 0.8
            idx_pass = np.where(power_arr >= target_power)[0]
            if len(idx_pass) > 0:
                first_pass = idx_pass[0]
                if first_pass > 0:
                    # Interpolate between first_pass-1 and first_pass
                    x0, x1 = slopes_arr[first_pass-1], slopes_arr[first_pass]
                    y0, y1 = power_arr[first_pass-1], power_arr[first_pass]

                    if y1 != y0:
                        # Linear interp: x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                        mdt = x0 + (target_power - y0) * (x1 - x0) / (y1 - y0)
                    else:
                        mdt = x0 # Should not happen if crossed
                else:
                    # Even the first point passed
                    mdt = slopes_arr[0]
        except Exception:
            pass

    df_results = pd.DataFrame(results)

    return PowerResult(
        slopes=slopes_arr,
        power=power_arr,
        min_detectable_trend=mdt,
        n_simulations=n_simulations,
        n_surrogates_inner=n_surrogates,
        alpha=alpha,
        simulation_results=df_results,
        noise_method=method_used
    )
