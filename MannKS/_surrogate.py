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

try:
    from astropy.timeseries import LombScargle
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

from ._stats import _mk_score_and_var_censored, _z_score, _p_value


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

    surrogates = np.empty((n_surrogates, n))

    for k in range(n_surrogates):
        # Initialize with random shuffle of data
        r = rng.permutation(x)

        prev_change = float('inf')

        for _ in range(max_iter):
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
            if change < tol or change >= prev_change:
                 r = r_new
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
    periodogram_method: Optional[str] = None
) -> np.ndarray:
    """
    Generates surrogates using Spectral Synthesis from Lomb-Scargle Periodogram.

    Suitable for UNEVENLY spaced data. Uses Astropy.

    Algorithm:
    1. Compute LS Periodogram P(f).
    2. Generate random phases phi ~ U[0, 2pi).
    3. Reconstruct time series at original time points t:
       x_surr(t) = sum( sqrt(P(f)) * cos(2*pi*f*t + phi) )
    4. Rank-adjust to match original value distribution (Gaussianization correction).

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

    Returns:
        np.ndarray: Array of surrogate time series.
    """
    if not HAS_ASTROPY:
        raise ImportError("`astropy` is required for Lomb-Scargle surrogates. Install it via `pip install astropy`.")

    rng = np.random.default_rng(random_state)
    n = len(x)

    # Pre-processing
    if center_data:
        x_centered = x - np.mean(x)
    else:
        x_centered = x

    # Warn about performance for large computations
    if n * n_surrogates > 2000000:
         warnings.warn(
            f"Lomb-Scargle surrogate generation is computationally expensive for N={n} "
            f"and n_surrogates={n_surrogates}. Expect significant runtime. "
            "Consider reducing n_surrogates or aggregating data.",
            UserWarning
        )

    # 1. Compute Lomb-Scargle Periodogram
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

         # Astropy 'fast' method requires regular frequency grid.
         # For log-spaced (irregular) frequency, we must use 'slow' or standard method.
         # 'cython' is the default standard method which handles arbitrary frequencies.
         if periodogram_method:
             method_to_use = periodogram_method
         else:
             method_to_use = 'cython'
         power = ls.power(freq, normalization=normalization, method=method_to_use)
    else:
        # User supplied array not fully supported in this simplified snippet, fallback to auto
        method_to_use = periodogram_method if periodogram_method else 'fast'
        freq, power = ls.autopower(normalization=normalization, method=method_to_use)

    # Convert power to amplitude for synthesis
    # Note: Normalization affects this scaling.
    # For 'standard' norm, Power is related to variance.
    # We use a heuristic: we just use sqrt(Power) as weights and then rescale the final series
    # to match the original variance/distribution exactly via rank mapping (step 4).
    # This avoids complex normalization reverse-engineering.
    amplitudes = np.sqrt(power)

    surrogates = np.empty((n_surrogates, n))

    # Store sorted original values for rank adjustment
    sorted_x = np.sort(x)

    for k in range(n_surrogates):
        # 2. Random Phases
        phases = rng.uniform(0, 2 * np.pi, size=len(freq))

        # 3. Spectral Synthesis
        # x_surr = Sum( A * cos(2pi*f*t + phi) )
        # Using broadcasting: (n_t, 1) * (1, n_f) -> (n_t, n_f) -> sum -> (n_t,)
        # For large N, this sum is slow. We can optimize.

        # Optimization: Process in chunks if N*N_freq is too large
        # But for typical usage (N < 10k), direct sum is okay.
        # Astropy's autopower usually returns ~5*N frequencies.
        # So N=1000 -> 5000 freq -> 5e6 ops. Fast.
        # N=10000 -> 50000 freq -> 5e8 ops. ~1 sec per surrogate.
        # For 1000 surrogates, this is too slow.

        # FAST SYNTHESIS APPROXIMATION required for large N.
        # However, since t is uneven, we CANNOT use IFFT easily.
        # We will stick to direct summation but limit frequencies if needed?
        # Or rely on the user to limit N for this expensive test.
        # Let's use a dot product which is optimized in BLAS.

        # Argument: 2 * pi * f * t + phi
        # Shapes: t (N,), f (M,), phi (M,)
        # We need sum over M.
        # arg = 2*pi * t[:, None] * freq[None, :] + phases[None, :]
        # This creates (N, M) array. 10k * 50k floats = 4GB RAM. Too big.

        # Chunked summation
        x_surr_raw = np.zeros(n)
        chunk_size = 1000 # Process 1000 frequencies at a time

        t_2pi = 2 * np.pi * t

        for i in range(0, len(freq), chunk_size):
            end = min(i + chunk_size, len(freq))
            f_chunk = freq[i:end]
            p_chunk = phases[i:end]
            a_chunk = amplitudes[i:end]

            # (N, 1) * (1, Chunk) + (1, Chunk)
            arg = t_2pi[:, np.newaxis] * f_chunk[np.newaxis, :] + p_chunk[np.newaxis, :]
            x_surr_raw += np.sum(a_chunk * np.cos(arg), axis=1)

        # 4. Rank Adjustment (IAAFT-like step for uneven data)
        # Replaces synthesized values with original values based on rank.
        # This preserves the marginal distribution exactly.
        rank_indices = np.argsort(np.argsort(x_surr_raw))
        surrogates[k, :] = sorted_x[rank_indices]

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
        **kwargs: Additional arguments passed to the underlying surrogate generator.

    Returns:
        SurrogateResult: Named tuple containing p-value, z-score, and details.
    """
    x_arr = np.asarray(x).flatten()
    t_arr = np.asarray(t).flatten()
    n = len(x_arr)

    if censored is None:
        censored = np.zeros_like(x_arr, dtype=bool)
    if cen_type is None:
        cen_type = np.full(x_arr.shape, 'not', dtype=object)

    notes = []

    if np.any(censored):
        warnings.warn(
            "Censored data detected in surrogate test. Surrogate series are generated "
            "using the numeric values (detection limits) as continuous input and are "
            "treated as uncensored. The null hypothesis test compares the original "
            "(censored) S statistic against a distribution of (uncensored) surrogate "
            "S statistics. This approximation may be biased if censoring is heavy.",
            UserWarning
        )
        notes.append("Censored data: surrogates treated as uncensored")

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
            x_arr, t_arr, dy=dy,
            n_surrogates=n_surrogates,
            freq_method=freq_method,
            normalization=normalization,
            fit_mean=fit_mean,
            center_data=center_data,
            random_state=random_state,
            **kwargs  # Pass any extra arguments to the implementation
        )
    elif method_used == 'iaaft':
        if not is_uniform and method != 'auto':
            warnings.warn("Using IAAFT on unevenly spaced data. Results may be biased.", UserWarning)

        surrogates = _iaaft_surrogates(
            x_arr,
            n_surrogates=n_surrogates,
            random_state=random_state
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

    # 2. Surrogate Scores
    surrogate_scores = np.zeros(n_surrogates)

    # Pre-allocate uncensored arrays for surrogates to avoid repeated creation
    surr_censored = np.zeros(n, dtype=bool)
    surr_cen_type = np.full(n, 'not', dtype=object)

    # Use simpler non-censored loop for speed if possible, but our _mk function is optimized
    # Ideally we'd have a vectorised MK for many arrays, but loop is acceptable here
    for i in range(n_surrogates):
        s_surr, _, _, _ = _mk_score_and_var_censored(
            surrogates[i], t_arr,
            censored=surr_censored,
            cen_type=surr_cen_type,
            mk_test_method=mk_test_method,
            tie_break_method=tie_break_method,
            tau_method=tau_method
        )
        surrogate_scores[i] = s_surr

    # Calculate Significance
    # Two-sided test: fraction of surrogates with |S| >= |S_orig|
    # Logic: If data is random red noise, how often do we see a trend this strong?

    n_extreme = np.sum(np.abs(surrogate_scores) >= np.abs(s_orig))
    p_value = n_extreme / n_surrogates

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
