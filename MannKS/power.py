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
from ._helpers import _preprocessing, _get_slope_scaling_factor

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
    slope_scaling: Optional[str]

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
    slope_scaling: Optional[str] = None,
    detrend: bool = False,
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
        slope_scaling (str, optional): The time unit for the provided slopes (e.g., 'year').
            If provided, input slopes are interpreted as 'units per [slope_scaling]' and
            converted to 'units per second' before injection.
            Supports: 's', 'min', 'h', 'D', 'Y' and their full names (e.g. 'year', 'day').
            Default is None (no conversion, interpreted as units per second or raw time unit).
        detrend (bool): If True, linearly detrends the input `x` before generating surrogates.
            This prevents an existing strong trend in `x` from inflating the low-frequency
            power of the noise model, which would otherwise reduce the estimated power.
            Default is False (conservative).
        **kwargs: Additional arguments passed to `surrogate_test`.

    Returns:
        PowerResult: Named tuple containing power curve, MDT, and details.
    """
    # Robustly handle DataFrame input for x
    if isinstance(x, pd.DataFrame):
        if 'value' in x.columns:
            x_arr = x['value'].to_numpy()
        elif x.shape[1] == 1:
            x_arr = x.iloc[:, 0].to_numpy()
        else:
            raise ValueError(
                "Input `x` is a DataFrame but has multiple columns and no 'value' column. "
                "Please provide a Series, 1D array, or DataFrame with a 'value' column."
            )
    else:
        x_arr = np.asarray(x).flatten()

    t_arr = np.asarray(t).flatten()

    # Convert t to numeric (float seconds if datetime) using internal helper
    t_numeric, _ = _preprocessing(t_arr)

    slopes_arr = np.asarray(slopes)

    # Validation
    if len(x_arr) != len(t_numeric):
        raise ValueError("x and t must have the same length.")

    surr_kwargs = surrogate_kwargs.copy() if surrogate_kwargs else {}
    surr_kwargs.update(kwargs)

    # Handle Slope Unit Conversion
    # _get_slope_scaling_factor returns Seconds/Unit.
    # User slope is Units/Unit.
    # We want Units/Second.
    # Units/Second = (Units/Unit) / (Seconds/Unit)

    scaling_divisor = 1.0
    if slope_scaling:
        try:
             scaling_divisor = _get_slope_scaling_factor(slope_scaling)
        except ValueError as e:
            # Re-raise with context or just let it bubble
            # To be safe and informative given the context of power_test:
            raise ValueError(f"Invalid `slope_scaling` parameter: {e}") from e

    slopes_scaled = slopes_arr / scaling_divisor

    # 1. Determine Method and Generate Base Noise Model
    # We generate 'n_simulations' *independent* noise realizations.
    # These represent the "Null" world (no deterministic trend, just colored noise).

    rng = np.random.default_rng(random_state)

    # Detrend if requested
    x_for_noise = x_arr
    if detrend:
        # Simple linear detrending using least squares for speed/robustness balance
        # We use t_numeric (seconds) for detrending
        # Fit y = m*t + c
        mask = np.isfinite(x_arr)
        if np.any(mask):
            A = np.vstack([t_numeric[mask], np.ones(np.sum(mask))]).T
            m, c = np.linalg.lstsq(A, x_arr[mask], rcond=None)[0]
            x_for_noise = x_arr - (m * t_numeric + c)
        else:
            x_for_noise = x_arr

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
            x_for_noise, t_numeric,
            n_surrogates=n_simulations,
            random_state=random_state,
            **gen_kwargs
        )
    elif method_used == 'iaaft':
        noise_bank = _iaaft_surrogates(
            x_for_noise,
            n_surrogates=n_simulations,
            random_state=random_state,
            # IAAFT accepts max_iter, tol in kwargs? No, explicit args.
            # We map from surr_kwargs if present
            max_iter=gen_kwargs.get('max_iter', 100),
            tol=gen_kwargs.get('tol', 1e-6)
        )
    else:
        raise ValueError(f"Unknown method '{method_used}'")

    # Check for computational complexity
    # Estimate total operations
    est_max_iter = surr_kwargs.get('max_iter', 100 if method_used == 'iaaft' else 1)
    # n_samples * n_surrogates * max_iter * n_simulations * n_slopes
    total_ops = len(x_arr) * n_surrogates * est_max_iter * n_simulations * len(slopes_scaled)

    # Threshold: 10 million operations for Lomb-Scargle (expensive) or 500M for IAAFT (faster)
    # LS is significantly slower per op due to trig/grid.
    limit = 10_000_000 if method_used == 'lomb_scargle' else 500_000_000

    if total_ops > limit:
         warnings.warn(
            f"Power analysis involves repeated surrogate generation which is computationally expensive "
            f"(approx {total_ops:.1e} operations). Expect significant runtime. "
            "Consider reducing n_simulations, n_surrogates, or using method='iaaft' if appropriate.",
            UserWarning
        )

    # 2. Monte Carlo Loop

    results = []

    # Center time for trend injection to avoid huge intercepts
    t_centered = t_numeric - np.mean(t_numeric)

    power_values = []

    # Prepare seeds if random_state is set
    # We need n_slopes * n_simulations seeds
    seeds = None
    if random_state is not None:
        # Create a new RNG derived from main seed to generate sub-seeds
        seed_rng = np.random.default_rng(random_state + 1)
        total_runs = len(slopes_scaled) * n_simulations
        seeds = seed_rng.integers(0, 2**32, size=total_runs)

    run_counter = 0

    for idx, beta in enumerate(slopes_scaled):
        n_detected = 0
        original_slope = slopes_arr[idx] # Keep track of user-facing slope

        # We assume the noise_bank has shape (n_simulations, n_samples)
        # For each realization...
        for i in range(n_simulations):
            noise = noise_bank[i]

            # Inject Trend
            x_sim = noise + beta * t_centered

            # Run Test
            # Determine seed for this run
            current_seed = None
            if seeds is not None:
                current_seed = int(seeds[run_counter])
            run_counter += 1

            # Note: We pass surrogate_kwargs to the test as well
            # The test will generate `n_surrogates` internal surrogates

            # We suppress specific warnings to avoid flooding stdout
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Censored data detected in surrogate test")
                warnings.filterwarnings("ignore", message="Lomb-Scargle surrogate generation is computationally expensive")
                warnings.filterwarnings("ignore", message="Uneven sampling detected but `astropy` not installed")
                warnings.filterwarnings("ignore", message="Using IAAFT on unevenly spaced data")

                res = surrogate_test(
                    x_sim, t_numeric,
                    method=method_used,
                    n_surrogates=n_surrogates,
                    # surrogate_test does not take alpha as argument
                    random_state=current_seed,
                    **surr_kwargs
                )

            # Check detection
            if res.p_value < alpha:
                n_detected += 1

        power = n_detected / n_simulations
        power_values.append(power)

        results.append({
            'slope': original_slope,
            'slope_scaled': beta,
            'power': power,
            'n_detected': n_detected,
            'n_simulations': n_simulations
        })

    power_arr = np.array(power_values)

    # 3. Calculate Minimum Detectable Trend (MDT) at 80% Power
    # We use linear interpolation looking for the 0.8 crossing.
    # Note: MDT is reported in original units (slopes_arr)

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
        noise_method=method_used,
        slope_scaling=slope_scaling
    )
