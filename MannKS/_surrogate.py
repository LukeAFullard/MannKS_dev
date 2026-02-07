"""
Surrogate data generation for hypothesis testing against colored noise.

This module provides methods to generate surrogate time series that preserve
specific statistical properties of the original data (e.g., power spectrum,
amplitude distribution) while randomizing phases.

Supported Methods:
1. IAAFT (Iterated Amplitude Adjusted Fourier Transform): For evenly spaced data.
2. Lomb-Scargle Spectral Synthesis: For unevenly spaced data (uses Astropy).
"""

import numpy as np
import warnings
from typing import Optional, Union, Tuple, NamedTuple, List
from scipy.stats import rankdata

try:
    from astropy.timeseries import LombScargle
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

from ._stats import _mk_score_and_var_censored, _z_score, _p_value
from ._datetime import _to_numeric_time


class SurrogateResult(NamedTuple):
    """Container for surrogate test results."""
    method: str
    original_score: float
    surrogate_scores: np.ndarray
    p_value: float
    z_score: float
    n_surrogates: int
    trend_significant: bool
    notes: List[str]


def _iaaft_surrogates(
    x: np.ndarray,
    n_surrogates: int = 1000,
    max_iter: int = 100,
    tol: float = 1e-6,
    random_state: Optional[int] = None
) -> np.ndarray:
    """
    Generates surrogates using Iterated Amplitude Adjusted Fourier Transform (IAAFT).

    Preserves both the amplitude distribution and the power spectrum of the original data.
    Suitable for EVENLY spaced data.

    Ref: Schreiber, T., & Schmitz, A. (1996). Improved surrogate data for nonlinearity tests.

    Args:
        x (np.ndarray): Input time series.
        n_surrogates (int): Number of surrogates to generate.
        max_iter (int): Maximum iterations for IAAFT convergence.
        tol (float): Convergence tolerance.
        random_state (Optional[int]): Seed for reproducibility.

    Returns:
        np.ndarray: Array of surrogate time series (shape: n_surrogates x n).
    """
    rng = np.random.default_rng(random_state)
    n = len(x)

    # 1. Store original amplitude distribution (sorted) and power spectrum amplitude
    sorted_x = np.sort(x)
    fft_x = np.fft.rfft(x)
    amp_x = np.abs(fft_x)
    var_x = np.var(x)
    if var_x < 1e-9:
        var_x = 1.0 # Prevent division by zero for constant data

    surrogates = np.empty((n_surrogates, n))

    for k in range(n_surrogates):
        # Initialize with random shuffle of data
        r = rng.permutation(x)

        prev_change = float('inf')

        for i in range(max_iter):
            # Step 1: Enforce Power Spectrum
            # Take FFT, replace amplitudes with original amp_x, keep phases
            fft_r = np.fft.rfft(r)
            phases = np.angle(fft_r)

            # Reconstruct with original amplitudes and current phases
            new_fft = amp_x * np.exp(1j * phases)
            s = np.fft.irfft(new_fft, n=n)

            # Step 2: Enforce Amplitude Distribution
            # Replace values in s with values from sorted_x based on rank
            rank_indices = np.argsort(np.argsort(s)) # Get ranks (0 to n-1)
            r_new = sorted_x[rank_indices]

            # Check convergence (mean squared change)
            change = np.mean((r_new - r)**2)
            rel_change = change / var_x

            if rel_change < tol:
                 r = r_new
                 break

            if change >= prev_change:
                 # Check relative change to avoid scale-dependent warnings
                 if rel_change > max(tol, 1e-3):
                     warnings.warn(f"IAAFT convergence stalled at iter {i} (rel_change={rel_change:.2e}). Result may be suboptimal.", UserWarning)
                 # Keep previous r (better), discard r_new
                 break

            r = r_new
            prev_change = change

        surrogates[k, :] = r

    return surrogates


def _lomb_scargle_surrogates(
    x: np.ndarray,
    t: np.ndarray,
    dy: Optional[np.ndarray] = None,
    n_surrogates: int = 1000,
    freq_method: str = 'auto',
    normalization: str = 'standard',
    fit_mean: bool = True,
    center_data: bool = True,
    random_state: Optional[int] = None,
    periodogram_method: Optional[str] = None,
    max_iter: int = 1,
    tol: float = 0.01,
    **kwargs
) -> np.ndarray:
    """
    Generates surrogates using Spectral Synthesis from Lomb-Scargle Periodogram.

    Suitable for UNEVENLY spaced data. Uses Astropy.
    Can be iterative (max_iter > 1) to correct for spectral whitening caused by rank adjustment.

    Args:
        x (np.ndarray): Input data values.
        t (np.ndarray): Input time values.
        dy (Optional[np.ndarray]): Measurement uncertainties.
        n_surrogates (int): Number of surrogates to generate.
        freq_method (str): 'auto' or 'log' for frequency grid selection.
        normalization (str): Periodogram normalization ('standard', 'model', 'log', 'psd').
        fit_mean (bool): Whether to fit a floating mean during periodogram calculation.
        center_data (bool): Whether to center data before analysis.
        random_state (Optional[int]): Seed for reproducibility.
        periodogram_method (Optional[str]): Astropy method (e.g., 'fast', 'slow', 'cython').
                                          If None, defaults to 'fast' for 'auto' freq_method.
        max_iter (int): Maximum iterations for spectral correction. Default 1 (non-iterative).
        tol (float): Convergence tolerance (unused in current implementation, reserved for future).
        **kwargs: Additional arguments (ignored, but allowed for flexibility).

    Returns:
        np.ndarray: Array of surrogate time series.
    """
    if not HAS_ASTROPY:
        raise ImportError("`astropy` is required for Lomb-Scargle surrogates. Install it via `pip install astropy`.")

    rng = np.random.default_rng(random_state)
    n = len(x)
    sorted_x = np.sort(x)

    # Pre-processing
    if center_data:
        x_centered = x - np.mean(x)
    else:
        x_centered = x

    if max_iter < 1:
        raise ValueError("`max_iter` must be at least 1.")

    # Check for constant data (zero variance)
    # If data is constant, Lomb-Scargle fails or produces NaNs (division by zero power).
    # Surrogates of constant data should be constant.
    if np.std(x) < 1e-9:
        return np.tile(x, (n_surrogates, 1))

    # Warn about performance for large computations
    if n * n_surrogates * max_iter > 2000000:
         warnings.warn(
            f"Lomb-Scargle surrogate generation is computationally expensive for N={n} "
            f"n_surrogates={n_surrogates} and max_iter={max_iter}. Expect significant runtime. "
            "Consider reducing n_surrogates, max_iter, or aggregating data.",
            UserWarning
        )

    # 1. Compute Lomb-Scargle Periodogram of Original Data (Target)
    ls = LombScargle(t, x_centered, dy=dy, fit_mean=fit_mean, center_data=False) # centering handled above or by fit_mean

    # Auto-frequency selection
    if freq_method == 'auto':
        method_to_use = periodogram_method if periodogram_method else 'fast'
        freq, power = ls.autopower(normalization=normalization, method=method_to_use)
    elif freq_method == 'log':
         # Heuristic for log-spacing (good for red noise)
         min_freq = 1 / (np.max(t) - np.min(t))
         max_freq = n / (2 * np.mean(np.diff(np.sort(t)))) # Nyquist approx
         freq = np.geomspace(min_freq, max_freq, num=n*2)

         if periodogram_method:
             method_to_use = periodogram_method
         else:
             method_to_use = 'cython'
         power = ls.power(freq, normalization=normalization, method=method_to_use)
    else:
        method_to_use = periodogram_method if periodogram_method else 'fast'
        freq, power = ls.autopower(normalization=normalization, method=method_to_use)

    # Target amplitudes (sqrt of power)
    # This is a heuristic for synthesis.
    amplitudes_target = np.sqrt(np.maximum(power, 0))

    surrogates = np.empty((n_surrogates, n))

    # Use zero-started time for synthesis to preserve numerical precision in cosine arguments
    t_shift = t - np.min(t)
    t_2pi = 2 * np.pi * t_shift

    for k in range(n_surrogates):
        # Random Phases
        phases = rng.uniform(0, 2 * np.pi, size=len(freq))

        # Initialize input amplitudes for synthesis with target amplitudes
        A_k = amplitudes_target.copy()

        # Iterative Loop
        # If max_iter=1, this runs once (standard method)
        for i_iter in range(max_iter):
            # A. Synthesis
            # x_surr = Sum( A * cos(2pi*f*t + phi) )

            x_synth = np.zeros(n)

            # Memory Optimization (Issue #10)
            # Reduce chunk size based on N to keep memory usage < 100MB per batch
            # Memory per batch = N * chunk_size * 8 bytes
            # Target 100MB = 100 * 10^6 bytes / 8 = 12.5M elements
            # chunk_size = 12.5M / N
            safe_elements = 12_500_000
            chunk_size = max(10, int(safe_elements / max(1, n)))
            chunk_size = min(chunk_size, 1000) # Cap at 1000 for reasonable frequency batches

            for j in range(0, len(freq), chunk_size):
                end = min(j + chunk_size, len(freq))
                f_chunk = freq[j:end]
                p_chunk = phases[j:end]
                a_chunk = A_k[j:end]

                # (N, 1) * (1, Chunk) + (1, Chunk)
                arg = t_2pi[:, np.newaxis] * f_chunk[np.newaxis, :] + p_chunk[np.newaxis, :]
                x_synth += np.sum(a_chunk * np.cos(arg), axis=1)

            # B. Rank Adjustment
            # Replaces synthesized values with original values based on rank.
            rank_indices = np.argsort(np.argsort(x_synth))
            x_adjusted = sorted_x[rank_indices]

            # If this is the last iteration, we are done
            if i_iter == max_iter - 1:
                surrogates[k, :] = x_adjusted
                break

            # C. Spectral Correction Step
            # Compare output spectrum to target spectrum and adjust input amplitudes

            # Compute LS of the ADJUSTED surrogate
            # Note: Must use 'cython' or similar that supports arbitrary freq grid to match exactly
            ls_out = LombScargle(t, x_adjusted, dy=dy, fit_mean=fit_mean, center_data=False)
            power_out = ls_out.power(freq, normalization=normalization, method='cython')
            amplitudes_out = np.sqrt(power_out)

            # Correction factor: A_in_new = A_in_old * (A_target / A_out)^0.8
            # (Power 0.8 is a damping factor found to be stable)
            ratio = (amplitudes_target + 1e-9) / (amplitudes_out + 1e-9)
            A_k = A_k * np.power(ratio, 0.8)

    return surrogates


def surrogate_test(
    x: Union[np.ndarray, "pd.DataFrame"], # type: ignore
    t: np.ndarray,
    censored: Optional[np.ndarray] = None,
    cen_type: Optional[np.ndarray] = None,
    dy: Optional[np.ndarray] = None,
    method: str = 'auto',
    n_surrogates: int = 1000,
    random_state: Optional[int] = None,
    mk_test_method: str = 'lwp',
    tie_break_method: str = 'lwp',
    tau_method: str = 'b',
    # Advanced Parameters
    freq_method: str = 'auto',
    normalization: str = 'standard',
    fit_mean: bool = True,
    center_data: bool = True,
    max_iter: int = 1,
    lt_mult: float = 0.5,
    gt_mult: float = 1.1,
    **kwargs
) -> SurrogateResult:
    """
    Performs a trend significance test using surrogate data.

    Comparison of the original Mann-Kendall S statistic against a null distribution
    generated from surrogate time series that preserve the data's autocorrelation
    (power spectrum) and amplitude distribution.

    Args:
        x (Union[np.ndarray, pd.DataFrame]): Data values.
        t (np.ndarray): Time values.
        censored (Optional[np.ndarray]): Boolean array indicating censoring.
        cen_type (Optional[np.ndarray]): Array of censoring types.
        dy (Optional[np.ndarray]): Measurement uncertainties (used only for Lomb-Scargle method).
        method (str): Surrogate generation method ('auto', 'iaaft', 'lomb_scargle').
            - 'auto': Selects 'iaaft' if time steps are uniform, 'lomb_scargle' otherwise.
            - 'iaaft': Iterated Amplitude Adjusted Fourier Transform (requires even sampling).
            - 'lomb_scargle': Spectral synthesis via Astropy (handles uneven sampling).
        n_surrogates (int): Number of surrogate datasets to generate.
        random_state (Optional[int]): Seed for reproducibility.
        mk_test_method (str): Method for MK test score calculation.
        tie_break_method (str): Method for breaking ties in timestamps.
        tau_method (str): Method for Kendall's Tau calculation.
        freq_method (str): (Lomb-Scargle only) 'auto' or 'log'.
        normalization (str): (Lomb-Scargle only) Periodogram normalization.
        fit_mean (bool): (Lomb-Scargle only) Fit a floating mean during periodogram calculation.
        center_data (bool): (Lomb-Scargle only) Center data before analysis.
        max_iter (int): (Lomb-Scargle only) Max iterations for spectral correction. Default 1.
        lt_mult (float): Multiplier for left-censored data (default 0.5).
        gt_mult (float): Multiplier for right-censored data (default 1.1).
        **kwargs: Additional arguments passed to the underlying surrogate generator.

    Returns:
        SurrogateResult: Named tuple containing p-value, z-score, and details.
    """
    x_arr = np.asarray(x).flatten()
    t_arr = _to_numeric_time(t).flatten()
    n = len(x_arr)

    if censored is None:
        censored = np.zeros_like(x_arr, dtype=bool)
    if cen_type is None:
        cen_type = np.full(x_arr.shape, 'not', dtype=object)

    notes = []

    # Apply imputation if censored data is present
    x_eff = x_arr.copy().astype(float)
    if np.any(censored):
        # We need to distinguish between left and right censoring if possible
        # Typically 'cen_type' handles this: 'lt', 'gt', 'not'
        # Default behavior if cen_type is not specific? _mk_score... uses it.
        # Here we manually apply substitution.

        lt_mask = censored & (cen_type == 'lt')
        gt_mask = censored & (cen_type == 'gt')

        # Fallback: if cen_type is all 'not' but censored is True, assume 'lt'?
        # Or check if cen_type contains ANY 'lt' or 'gt'.
        # Most project helpers assume 'lt' if unspecified for boolean masked arrays.
        if not np.any(lt_mask) and not np.any(gt_mask):
             # Assume all censored are 'lt' (standard environmental default)
             lt_mask = censored

        if np.any(lt_mask):
            x_eff[lt_mask] *= lt_mult
        if np.any(gt_mask):
            x_eff[gt_mask] *= gt_mult

        warnings.warn(
            f"Censored data detected in surrogate test. Surrogate series are generated "
            f"using imputed values (lt_mult={lt_mult}, gt_mult={gt_mult}). "
            "Censoring flags are propagated to the surrogates to ensure a consistent S-statistic distribution.",
            UserWarning
        )
        notes.append(f"Censored data: surrogates generated from imputed values ({lt_mult}x/{gt_mult}x)")
    else:
        # No censored data, x_eff is just x_arr
        pass

    if n_surrogates <= 0:
        raise ValueError("`n_surrogates` must be positive.")

    # Check for uneven sampling
    dt = np.diff(t_arr)
    is_uniform = np.allclose(dt, dt[0], rtol=1e-3)

    if method == 'auto':
        if is_uniform:
            method_used = 'iaaft'
        else:
            if HAS_ASTROPY:
                method_used = 'lomb_scargle'
            else:
                warnings.warn(
                    "Uneven sampling detected but `astropy` not installed. "
                    "Falling back to 'iaaft' (may be inaccurate). "
                    "Install astropy for robust uneven handling.",
                    UserWarning
                )
                method_used = 'iaaft'
                notes.append("Uneven sampling with IAAFT fallback")
    else:
        method_used = method

    # Generate Surrogates
    if method_used == 'lomb_scargle':
        if not HAS_ASTROPY:
             raise ImportError("Method 'lomb_scargle' requires `astropy`.")

        surrogates = _lomb_scargle_surrogates(
            x_eff, t_arr, dy=dy,
            n_surrogates=n_surrogates,
            freq_method=freq_method,
            normalization=normalization,
            fit_mean=fit_mean,
            center_data=center_data,
            random_state=random_state,
            max_iter=max_iter,
            **kwargs  # Pass any extra arguments to the implementation
        )
    elif method_used == 'iaaft':
        if not is_uniform and method != 'auto':
            warnings.warn("Using IAAFT on unevenly spaced data. Results may be biased.", UserWarning)

        # Propagate max_iter (explicit arg) and tol (from kwargs) to IAAFT.
        # Note: surrogate_test defaults max_iter=1 (suitable for Lomb-Scargle standard mode),
        # but IAAFT requires iterative refinement (default 100).
        # If max_iter is left at 1 (the default), we override it to 100 for IAAFT
        # to ensure convergence unless the user explicitly requested a different value (implied by != 1).

        iaaft_max_iter = max_iter
        if max_iter == 1:
            iaaft_max_iter = 100

        surrogates = _iaaft_surrogates(
            x_eff,
            n_surrogates=n_surrogates,
            random_state=random_state,
            max_iter=iaaft_max_iter,
            tol=kwargs.get('tol', 1e-6)
        )
    else:
        raise ValueError(f"Unknown method '{method}'.")

    # Calculate MK Statistics
    # We use the robust standard calculation for all series

    # 1. Original Score
    s_orig, _, _, _ = _mk_score_and_var_censored(
        x_arr, t_arr,
        censored=censored,
        cen_type=cen_type,
        mk_test_method=mk_test_method,
        tie_break_method=tie_break_method,
        tau_method=tau_method
    )

    # Consistency Check for Censored Data
    if np.any(censored):
        # Calculate S using the imputed values (x_eff) used for surrogate generation
        s_imputed, _, _, _ = _mk_score_and_var_censored(
            x_eff, t_arr,
            censored=censored,
            cen_type=cen_type,
            mk_test_method=mk_test_method,
            tie_break_method=tie_break_method,
            tau_method=tau_method
        )

        # If the rank structure of the imputed data differs from the raw data
        # (e.g. because lt_mult resolves ambiguities that were ties), warn the user.
        if not np.isclose(s_orig, s_imputed, atol=1e-5):
             warnings.warn(
                 f"Imputation with lt_mult={lt_mult} changes the Mann-Kendall S statistic "
                 f"(Raw: {s_orig}, Imputed: {s_imputed}). "
                 "The p-value is calculated using the Raw S statistic against surrogates derived from "
                 "the Imputed data. This may lead to conservative results if imputation resolves "
                 "ambiguities present in the raw data.",
                 UserWarning
             )

    # 2. Surrogate Scores
    surrogate_scores = np.zeros(n_surrogates)

    # Prepare for censoring propagation
    if np.any(censored):
        # Sort original data/censoring by imputed values to create a map
        sort_idx = np.argsort(x_eff, kind='stable')
        sorted_censored = censored[sort_idx]
        sorted_cen_type = cen_type[sort_idx]
    else:
        # Defaults for uncensored case
        surr_censored = np.zeros(n, dtype=bool)
        surr_cen_type = np.full(n, 'not', dtype=object)

    for i in range(n_surrogates):
        row = surrogates[i]

        if np.any(censored):
            # Map censoring status to the surrogate values
            # rankdata(method='ordinal') returns ranks 1..N
            # We use these ranks to index into the sorted censoring arrays
            ranks = rankdata(row, method='ordinal') - 1
            # Ensure ranks are within bounds (should be 0..N-1) and integer type
            ranks = np.clip(ranks, 0, n - 1).astype(int)

            s_cen = sorted_censored[ranks]
            s_type = sorted_cen_type[ranks]
        else:
            s_cen = surr_censored
            s_type = surr_cen_type

        s_surr, _, _, _ = _mk_score_and_var_censored(
            row, t_arr,
            censored=s_cen,
            cen_type=s_type,
            mk_test_method=mk_test_method,
            tie_break_method=tie_break_method,
            tau_method=tau_method,
            calc_var=False
        )
        surrogate_scores[i] = s_surr

    # Calculate Significance
    # Two-sided test: fraction of surrogates with |S| >= |S_orig|
    # Logic: If data is random red noise, how often do we see a trend this strong?

    n_extreme = np.sum(np.abs(surrogate_scores) >= np.abs(s_orig))
    p_value = (n_extreme + 1) / (n_surrogates + 1)

    # Z-score relative to surrogate distribution
    mean_s = np.mean(surrogate_scores)
    std_s = np.std(surrogate_scores, ddof=1)

    if std_s > 0:
        z_score = (s_orig - mean_s) / std_s
    else:
        z_score = 0.0

    trend_significant = p_value < 0.05 # Simple threshold check

    return SurrogateResult(
        method=method_used,
        original_score=s_orig,
        surrogate_scores=surrogate_scores,
        p_value=p_value,
        z_score=z_score,
        n_surrogates=n_surrogates,
        trend_significant=trend_significant,
        notes=notes
    )
