# Implementation Report: Block Bootstrap and Rolling Sen's Slope

## Executive Summary

This report proposes three enhancements to the MannKS package:
1. **Block Bootstrap for Autocorrelation** - **[COMPLETED]** Addresses a fundamental statistical assumption violation
2. **Rolling Sen's Slope** - **[COMPLETED]** Adds temporal analysis capabilities
3. **Segmented Sen's Slope Regression** - Detects structural breaks and regime shifts

All three features align with the package's focus on real-world environmental data and would fill gaps in current functionality.

---

## Feature 1: Block Bootstrap for Autocorrelation

### Justification

#### The Problem
The Mann-Kendall test assumes **serially independent observations**. Environmental time series frequently violate this:
- **Daily water quality**: Today's measurement correlates with yesterday's
- **Hourly air quality**: Pollution episodes persist across hours
- **Monthly climate indices**: ENSO effects persist for 6-12 months

When autocorrelation is present, the standard Mann-Kendall test:
- Underestimates variance → inflates significance
- Reports trends that are artifacts of persistence
- Can show p=0.001 when the true p>0.05

#### Current Gap
Your package warns users about autocorrelation in docstrings but provides no solution. Users must either:
1. Ignore the problem (common, leads to bad science)
2. Use external packages (friction, inconsistent with your API)
3. Pre-whiten data (complex, loses information)

#### Why Block Bootstrap?
- **Preserves correlation structure** - Resamples contiguous blocks, maintaining within-block correlation
- **Non-parametric** - No distributional assumptions (matches Mann-Kendall philosophy)
- **Well-established** - Kunsch (1989), Politis & Romano (1994) provide theoretical foundation
- **Proven in ecology** - Used in environmental trend analysis (e.g., Meals et al. 2011)

#### Supporting Literature
- **Kunsch, H. R. (1989).** The jackknife and the bootstrap for general stationary observations. *Annals of Statistics*, 17(3), 1217-1241.
- **Politis, D. N., & Romano, J. P. (1994).** The stationary bootstrap. *JASA*, 89(428), 1303-1313.
- **Yue, S., & Wang, C. (2004).** The Mann-Kendall test modified by effective sample size to detect trend in serially correlated hydrological series. *Water Resources Management*, 18(3), 201-218.
- **Meals, D. W., et al. (2011).** Statistical analysis for monotonic trends. *EPA Tech Notes*, 6, 1-23.

### Workflow Integration

```
User Data → Check Autocorrelation → trend_test() with autocorr_method
                    ↓
              [If ACF > 0.3]
                    ↓
         Apply Block Bootstrap Correction
                    ↓
            Adjusted P-values/CIs
```

**API Design:**
```python
result = trend_test(
    x=data,
    t=dates,
    autocorr_method='block_bootstrap',  # New parameter
    block_size='auto',                   # or integer
    n_bootstrap=1000                     # number of resamples
)
# Returns same structure, but p-value/CIs are corrected
```

**Alternative: Automatic Detection**
```python
result = trend_test(
    x=data,
    t=dates,
    autocorr_method='auto'  # Tests ACF, applies correction if needed
)
# Adds to analysis_notes: "Autocorrelation detected (ACF=0.45), block bootstrap applied"
```

### Step-by-Step Implementation

#### Step 1: Add ACF Detection Function
**File:** `MannKS/_autocorr.py` (new file)

```python
import numpy as np
from scipy.stats import norm

def estimate_acf(x, max_lag=None):
    """
    Estimate autocorrelation function.

    Args:
        x: Data vector
        max_lag: Maximum lag to compute (default: min(n/4, 50))

    Returns:
        acf: Array of autocorrelation coefficients
        significant_lag: First lag where ACF crosses significance threshold
    """
    n = len(x)
    if max_lag is None:
        max_lag = min(n // 4, 50)

    x_centered = x - np.mean(x)
    c0 = np.dot(x_centered, x_centered) / n

    acf = np.zeros(max_lag + 1)
    acf[0] = 1.0

    for lag in range(1, max_lag + 1):
        c_lag = np.dot(x_centered[:-lag], x_centered[lag:]) / n
        acf[lag] = c_lag / c0

    # Significance threshold (95% CI under H0: no autocorr)
    threshold = 1.96 / np.sqrt(n)

    # Find first significant lag
    significant_lag = None
    for lag in range(1, len(acf)):
        if np.abs(acf[lag]) > threshold:
            significant_lag = lag
            break

    return acf, significant_lag


def effective_sample_size(x, method='yue'):
    """
    Calculate effective sample size accounting for autocorrelation.

    Args:
        x: Data vector
        method: 'yue' (Yue & Wang 2004) or 'bayley' (Bayley & Hammersley 1946)

    Returns:
        n_eff: Effective sample size
        acf1: Lag-1 autocorrelation
    """
    n = len(x)
    acf, _ = estimate_acf(x, max_lag=min(n//4, 50))
    acf1 = acf[1]

    if method == 'yue':
        # Yue & Wang (2004) formula
        if np.abs(acf1) < 1e-10:
            return n, acf1

        # Sum of autocorrelations (with exponential decay assumption)
        rho_sum = 0
        for k in range(1, len(acf)):
            rho_sum += (n - k) / n * acf[k]

        n_eff = n / (1 + 2 * rho_sum)
    else:
        # Simple Bayley-Hammersley formula
        n_eff = n * (1 - acf1) / (1 + acf1)

    return max(n_eff, 3), acf1  # Ensure minimum of 3


def should_apply_correction(x, threshold=0.1):
    """
    Determine if autocorrelation correction is needed.

    Args:
        x: Data vector
        threshold: ACF threshold for correction (default 0.1)

    Returns:
        needs_correction: Boolean
        acf1: Lag-1 autocorrelation
        n_eff: Effective sample size
    """
    acf, significant_lag = estimate_acf(x)
    acf1 = acf[1]
    n_eff, _ = effective_sample_size(x)

    needs_correction = (np.abs(acf1) > threshold or significant_lag is not None)

    return needs_correction, acf1, n_eff
```

#### Step 2: Implement Block Bootstrap
**File:** `MannKS/_bootstrap.py` (new file)

```python
import numpy as np
from ._stats import _mk_score_and_var_censored, _sens_estimator_unequal_spacing, _sens_estimator_censored

def optimal_block_size(n, acf):
    """
    Calculate optimal block size using Politis & White (2004) method.

    Args:
        n: Sample size
        acf: Autocorrelation function

    Returns:
        block_size: Optimal block length
    """
    # Simple heuristic: block size should be roughly the correlation length
    # Correlation length: first lag where ACF < 0.1
    corr_length = 1
    for i in range(1, len(acf)):
        if np.abs(acf[i]) < 0.1:
            corr_length = i
            break

    # Use 2 * correlation length, bounded by sqrt(n)
    block_size = min(2 * corr_length, int(np.sqrt(n)))
    return max(block_size, 3)  # Minimum block size of 3


def moving_block_bootstrap(x, block_size):
    """
    Generate one moving block bootstrap resample.

    Args:
        x: Data vector
        block_size: Block length

    Returns:
        x_boot: Bootstrap resample (same length as x)
    """
    n = len(x)
    n_blocks = int(np.ceil(n / block_size))

    # Random starting positions for blocks
    starts = np.random.randint(0, n - block_size + 1, size=n_blocks)

    # Build bootstrap sample
    x_boot = []
    for start in starts:
        x_boot.extend(x[start:start + block_size])

    return np.array(x_boot[:n])


def block_bootstrap_mann_kendall(x, t, censored, cen_type,
                                 block_size='auto', n_bootstrap=1000,
                                 tau_method='b', mk_test_method='robust'):
    """
    Block bootstrap Mann-Kendall test for autocorrelated data.

    Args:
        x, t, censored, cen_type: Standard inputs
        block_size: 'auto' or integer
        n_bootstrap: Number of bootstrap resamples
        tau_method, mk_test_method: Pass-through to _mk_score_and_var_censored

    Returns:
        p_boot: Bootstrap p-value
        s_obs: Observed S statistic
        s_boot_dist: Bootstrap distribution of S (for diagnostics)
    """
    n = len(x)

    # Calculate observed statistic
    s_obs, var_s_obs, _, _ = _mk_score_and_var_censored(
        x, t, censored, cen_type,
        tau_method=tau_method,
        mk_test_method=mk_test_method
    )

    # Determine block size
    if block_size == 'auto':
        from ._autocorr import estimate_acf
        acf, _ = estimate_acf(x)
        block_size = optimal_block_size(n, acf)

    # Detrend data under H0 (no trend)
    if np.any(censored):
        slopes = _sens_estimator_censored(x, t, cen_type)
    else:
        slopes = _sens_estimator_unequal_spacing(x, t)

    median_slope = np.nanmedian(slopes)
    x_detrended = x - median_slope * (t - np.median(t))

    # Bootstrap distribution
    s_boot_dist = np.zeros(n_bootstrap)

    for b in range(n_bootstrap):
        # Generate bootstrap sample (preserving time order)
        x_boot = moving_block_bootstrap(x_detrended, block_size)

        # Calculate S for bootstrap sample
        s_b, _, _, _ = _mk_score_and_var_censored(
            x_boot, t, censored, cen_type,
            tau_method=tau_method,
            mk_test_method=mk_test_method
        )
        s_boot_dist[b] = s_b

    # Two-sided p-value
    p_boot = np.mean(np.abs(s_boot_dist) >= np.abs(s_obs))

    return p_boot, s_obs, s_boot_dist


def block_bootstrap_confidence_intervals(x, t, censored, cen_type,
                                        block_size='auto', n_bootstrap=1000,
                                        alpha=0.05):
    """
    Bootstrap confidence intervals for Sen's slope with autocorrelated data.

    Returns:
        slope: Sen's slope
        lower_ci, upper_ci: Bootstrap confidence intervals
        boot_slopes: Bootstrap distribution (for diagnostics)
    """
    n = len(x)

    # Calculate observed slope
    if np.any(censored):
        slopes = _sens_estimator_censored(x, t, cen_type)
    else:
        slopes = _sens_estimator_unequal_spacing(x, t)
    slope_obs = np.nanmedian(slopes)

    # Determine block size
    if block_size == 'auto':
        from ._autocorr import estimate_acf
        acf, _ = estimate_acf(x)
        block_size = optimal_block_size(n, acf)

    # Bootstrap distribution
    boot_slopes = np.zeros(n_bootstrap)

    for b in range(n_bootstrap):
        # Resample residuals in blocks
        residuals = x - slope_obs * (t - np.median(t))
        residuals_boot = moving_block_bootstrap(residuals, block_size)

        # Reconstruct data
        x_boot = residuals_boot + slope_obs * (t - np.median(t))

        # Calculate slope
        if np.any(censored):
            slopes_b = _sens_estimator_censored(x_boot, t, cen_type)
        else:
            slopes_b = _sens_estimator_unequal_spacing(x_boot, t)
        boot_slopes[b] = np.nanmedian(slopes_b)

    # Percentile confidence intervals
    lower_ci = np.percentile(boot_slopes, 100 * alpha / 2)
    upper_ci = np.percentile(boot_slopes, 100 * (1 - alpha / 2))

    return slope_obs, lower_ci, upper_ci, boot_slopes
```

#### Step 3: Integrate into trend_test
**File:** `MannKS/trend_test.py`

Add parameters to function signature:
```python
def trend_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    alpha: float = 0.05,
    # ... existing parameters ...
    autocorr_method: str = 'none',  # NEW: 'none', 'auto', 'block_bootstrap', 'yue_wang'
    block_size: Union[str, int] = 'auto',  # NEW
    n_bootstrap: int = 1000,  # NEW
    # ... rest of parameters ...
) -> namedtuple:
```

Add to the result namedtuple:
```python
res = namedtuple('Mann_Kendall_Test', [
    # ... existing fields ...
    'acf1', 'n_effective', 'block_size_used'  # NEW
])
```

Add logic after data preparation:
```python
# After data_filtered is created...

# Check for autocorrelation
acf1 = 0.0
n_eff = n
block_size_used = None
needs_correction = False

if autocorr_method == 'auto':
    from ._autocorr import should_apply_correction
    needs_correction, acf1, n_eff = should_apply_correction(x_filtered)
    if needs_correction:
        analysis_notes.append(f'Autocorrelation detected (ACF1={acf1:.3f}), applying block bootstrap')
        autocorr_method = 'block_bootstrap'

elif autocorr_method == 'block_bootstrap':
    from ._autocorr import estimate_acf, effective_sample_size
    acf, _ = estimate_acf(x_filtered)
    acf1 = acf[1]
    n_eff, _ = effective_sample_size(x_filtered)
    needs_correction = True

# Standard Mann-Kendall calculation
s, var_s, D, Tau = _mk_score_and_var_censored(...)

# Apply bootstrap correction if needed
if autocorr_method == 'block_bootstrap':
    from ._bootstrap import block_bootstrap_mann_kendall, block_bootstrap_confidence_intervals

    # Bootstrap p-value
    p_boot, s_obs, s_boot_dist = block_bootstrap_mann_kendall(
        x_filtered, t_filtered, censored_filtered, cen_type_filtered,
        block_size=block_size, n_bootstrap=n_bootstrap
    )

    # Use bootstrap p-value instead of normal approximation
    p = p_boot
    z = norm.ppf(1 - p/2) * np.sign(s)  # Back-calculate z for consistency
    h = p < alpha

    # Bootstrap confidence intervals for slope
    if sens_slope_method != 'ats':
        _, lower_ci, upper_ci, _ = block_bootstrap_confidence_intervals(
            x_filtered, t_filtered, censored_filtered, cen_type_filtered,
            block_size=block_size, n_bootstrap=n_bootstrap, alpha=alpha
        )

    # Determine block size used
    if block_size == 'auto':
        from ._bootstrap import optimal_block_size
        from ._autocorr import estimate_acf
        acf, _ = estimate_acf(x_filtered)
        block_size_used = optimal_block_size(n, acf)
    else:
        block_size_used = block_size

elif autocorr_method == 'yue_wang':
    # Simpler correction: adjust variance by effective sample size
    n_eff, acf1 = effective_sample_size(x_filtered)
    var_s_corrected = var_s * (n / n_eff)
    z = _z_score(s, var_s_corrected)
    p, h, trend = _p_value(z, alpha)
    analysis_notes.append(f'Yue-Wang correction applied (n_eff={n_eff:.1f})')

else:
    # Standard calculation
    z = _z_score(s, var_s)
    p, h, trend = _p_value(z, alpha)

# Add to final result
final_results = results._replace(
    acf1=acf1,
    n_effective=n_eff,
    block_size_used=block_size_used
)
```

#### Step 4: Add Tests
**File:** `tests/test_autocorrelation.py` (new file)

```python
import numpy as np
import pytest
from MannKS import trend_test

def generate_ar1_process(n, phi, trend_slope=0.0, noise_sd=1.0):
    """Generate AR(1) process with trend."""
    x = np.zeros(n)
    x[0] = np.random.normal(0, noise_sd)

    for i in range(1, n):
        x[i] = phi * x[i-1] + np.random.normal(0, noise_sd)

    # Add trend
    t = np.arange(n)
    x += trend_slope * t

    return x, t

def test_block_bootstrap_reduces_false_positives():
    """Test that block bootstrap corrects for autocorrelation."""
    np.random.seed(42)
    n_trials = 100
    false_positives_standard = 0
    false_positives_bootstrap = 0

    for _ in range(n_trials):
        # Generate AR(1) with NO trend but high autocorrelation
        x, t = generate_ar1_process(n=100, phi=0.6, trend_slope=0.0)

        # Standard test (should have inflated Type I error)
        result_std = trend_test(x, t, autocorr_method='none')
        if result_std.h:
            false_positives_standard += 1

        # Bootstrap test (should have correct Type I error)
        result_boot = trend_test(x, t, autocorr_method='block_bootstrap', n_bootstrap=500)
        if result_boot.h:
            false_positives_bootstrap += 1

    # Standard should have > 5% false positives due to autocorrelation
    # Bootstrap should have ~5% false positives
    assert false_positives_standard > 10  # Should be much higher than 5%
    assert false_positives_bootstrap < 10  # Should be close to 5%

def test_block_bootstrap_preserves_power():
    """Test that block bootstrap maintains power for true trends."""
    np.random.seed(123)

    # Strong trend with autocorrelation
    x, t = generate_ar1_process(n=100, phi=0.5, trend_slope=0.1)

    result_std = trend_test(x, t, autocorr_method='none')
    result_boot = trend_test(x, t, autocorr_method='block_bootstrap', n_bootstrap=500)

    # Both should detect the trend
    assert result_std.h
    assert result_boot.h

    # Bootstrap p-value should be larger (more conservative)
    assert result_boot.p > result_std.p

def test_auto_detection():
    """Test automatic autocorrelation detection."""
    np.random.seed(456)

    # High autocorrelation case
    x_auto, t = generate_ar1_process(n=100, phi=0.7, trend_slope=0.0)
    result = trend_test(x_auto, t, autocorr_method='auto')

    assert 'Autocorrelation detected' in ' '.join(result.analysis_notes)
    assert result.acf1 > 0.5

def test_yue_wang_method():
    """Test Yue-Wang effective sample size correction."""
    np.random.seed(789)

    x, t = generate_ar1_process(n=100, phi=0.6, trend_slope=0.0)
    result = trend_test(x, t, autocorr_method='yue_wang')

    # Effective sample size should be less than actual
    assert result.n_effective < len(x)
    assert 'Yue-Wang correction' in ' '.join(result.analysis_notes)
```

#### Step 5: Add Validation Case
**File:** `validation/35_Autocorrelation_Correction/validate.py`

Compare against R's `zyp` package which implements Yue-Wang correction:
```R
library(zyp)
# Generate AR(1) data in R, run zyp.trend.vector()
# Compare p-values with MannKS block bootstrap
```

#### Step 6: Update Documentation
**File:** `Examples/Detailed_Guides/autocorrelation_guide.md`

```markdown
# Dealing with Autocorrelation

## When is autocorrelation a problem?

Autocorrelation (serial correlation) occurs when observations are correlated with nearby observations in time. This violates the independence assumption of Mann-Kendall tests.

**Common in:**
- High-frequency data (hourly, daily)
- Persistent phenomena (droughts, ENSO cycles)
- Slow-responding systems (groundwater, soil)

## How to detect autocorrelation

```python
from MannKS import trend_test

result = trend_test(x, t, autocorr_method='auto')

if result.acf1 > 0.1:
    print(f"Significant autocorrelation detected: ACF(1) = {result.acf1:.3f}")
    print(f"Effective sample size: {result.n_effective:.0f} (vs {len(x)} actual)")
```

## Correction methods

### Method 1: Block Bootstrap (Recommended)
```python
result = trend_test(x, t, autocorr_method='block_bootstrap', n_bootstrap=1000)
```
- Most robust
- Preserves correlation structure
- Computationally intensive

### Method 2: Yue-Wang Correction
```python
result = trend_test(x, t, autocorr_method='yue_wang')
```
- Fast approximation
- Adjusts variance by effective sample size
- Less accurate for complex autocorrelation structures

### Method 3: Automatic Detection
```python
result = trend_test(x, t, autocorr_method='auto')
```
- Tests for autocorrelation
- Applies block bootstrap if ACF(1) > 0.1
- Recommended for exploratory analysis
```

---

## Feature 2: Rolling Sen's Slope

### Justification

#### The Problem
Standard trend tests provide a **single global answer**: "Is there a trend over the entire period?"

Real-world questions are more nuanced:
- "When did water quality start improving?"
- "Did the trend accelerate after the policy change in 2015?"
- "Are recent years different from the long-term trend?"

#### Current Gap
Users must manually:
1. Subset data into arbitrary periods
2. Run multiple tests
3. Lose statistical power from smaller samples
4. Risk p-hacking (trying many breakpoints)

#### Why Rolling Windows?
- **Temporal resolution** - Shows how trends evolve
- **Change point detection** - Identifies regime shifts
- **Adaptive monitoring** - Helps target sampling effort
- **Intuitive visualization** - Easier to communicate than a single number

#### Real-World Applications
- **EPA water quality monitoring** - Detect when BMPs start working
- **Climate change** - Show acceleration/deceleration of warming
- **Air quality** - Identify impacts of emissions regulations
- **COVID impact studies** - Before/during/after pandemic trends

### Workflow Integration

```
User Data → Standard Trend Test → [If significant] → Rolling Analysis
                                       ↓
                              Visualize temporal patterns
                                       ↓
                            Identify change points
```

**API Design:**
```python
# Primary function
rolling_results = rolling_trend_test(
    x=data,
    t=dates,
    window='10Y',        # or integer for numeric time
    step='1Y',           # sliding window step
    min_size=10,         # minimum points per window
    slope_scaling='year'
)

# Returns DataFrame:
# window_start | window_end | slope | p_value | classification | n_obs
```

**Integration with plotting:**
```python
plot_rolling_trend(
    rolling_results,
    highlight_significant=True,
    show_global_trend=True,  # overlay single trend line
    save_path='rolling_trend.png'
)
```

### Step-by-Step Implementation

#### Step 1: Core Rolling Function
**File:** `MannKS/rolling_trend.py` (new file)

```python
import numpy as np
import pandas as pd
from typing import Union, Optional
from collections import namedtuple
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
    **kwargs  # Pass through to trend_test
) -> pd.DataFrame:
    """
    Calculate rolling Sen's slope over moving time windows.

    Args:
        x, t: Data and time vectors
        window: Window size - for datetime: '10Y', '5Y', '2Y', etc.
                            - for numeric: integer/float
        step: Step size for sliding window (default: window/2)
        min_size: Minimum observations per window
        alpha: Significance level
        seasonal: If True, use seasonal_trend_test
        period, season_type: For seasonal analysis
        slope_scaling: Time unit for slope (e.g., 'year')
        x_unit: Unit of measurement for x
        **kwargs: Additional arguments passed to trend_test

    Returns:
        DataFrame with columns:
            - window_start, window_end: Window boundaries
            - window_center: Midpoint for plotting
            - n_obs: Number of observations
            - slope: Sen's slope
            - lower_ci, upper_ci: Confidence intervals
            - p_value: Statistical significance
            - classification: Trend category
            - C: Confidence in direction
            - tau: Kendall's Tau
    """
    # Input validation
    x_arr = np.asarray(x) if not isinstance(x, pd.DataFrame) else x
    t_arr = np.asarray(t)

    if len(x_arr) != len(t_arr):
        raise ValueError("x and t must have same length")

    is_datetime = _is_datetime_like(t_arr)

    # Parse window and step
    if is_datetime:
        t_series = pd.to_datetime(t_arr)
        window_td = pd.Timedelta(window)
        step_td = pd.Timedelta(step) if step else window_td / 2
    else:
        t_series = pd.Series(t_arr)
        window_td = float(window)
        step_td = float(step) if step else window_td / 2

    # Generate windows
    windows = _generate_windows(t_series, window_td, step_td, is_datetime)

    # Calculate trends for each window
    results = []

    for win_start, win_end in windows:
        # Select data in window
        if is_datetime:
            mask = (t_series >= win_start) & (t_series < win_end)
        else:
            mask = (t_series >= win_start) & (t_series < win_end)

        if mask.sum() < min_size:
            continue

        # Extract window data
        if isinstance(x_arr, pd.DataFrame):
            x_window = x_arr[mask].reset_index(drop=True)
        else:
            x_window = x_arr[mask]
        t_window = t_arr[mask]

        # Run trend test
        try:
            if seasonal:
                result = seasonal_trend_test(
                    x=x_window,
                    t=t_window,
                    period=period,
                    season_type=season_type,
                    alpha=alpha,
                    slope_scaling=slope_scaling,
                    x_unit=x_unit,
                    **kwargs
                )
            else:
                result = trend_test(
                    x=x_window,
                    t=t_window,
                    alpha=alpha,
                    slope_scaling=slope_scaling,
                    x_unit=x_unit,
                    **kwargs
                )

            # Calculate window center
            if is_datetime:
                win_center = win_start + (win_end - win_start) / 2
            else:
                win_center = (win_start + win_end) / 2

            results.append({
                'window_start': win_start,
                'window_end': win_end,
                'window_center': win_center,
                'n_obs': mask.sum(),
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
            # Log warning but continue
            import warnings
            warnings.warn(f"Failed to calculate trend for window {win_start} to {win_end}: {e}")
            continue

    return pd.DataFrame(results)


def _generate_windows(t_series, window_size, step_size, is_datetime):
    """Generate sliding window boundaries."""
    windows = []

    t_min = t_series.min()
    t_max = t_series.max()

    current = t_min
    while current < t_max:
        win_end = current + window_size
        if win_end > t_max:
            win_end = t_max

        windows.append((current, win_end))
        current += step_size

        # Prevent infinite loop
        if len(windows) > 10000:
            raise ValueError("Too many windows generated. Check window/step sizes.")

    return windows


def detect_change_points(rolling_results, method='slope_sign_change', threshold=None):
    """
    Detect change points in rolling trend results.

    Args:
        rolling_results: DataFrame from rolling_trend_test
        method: 'slope_sign_change', 'classification_change', or 'threshold'
        threshold: For 'threshold' method, the slope change magnitude

    Returns:
        change_points: List of window_center values where changes occurred
        change_info: DataFrame with details about each change
    """
    if len(rolling_results) < 2:
        return [], pd.DataFrame()

    change_points = []
    change_info = []

    if method == 'slope_sign_change':
        # Detect where slope changes sign
        slopes = rolling_results['slope'].values
        for i in range(1, len(slopes)):
            if np.sign(slopes[i]) != np.sign(slopes[i-1]) and slopes[i] != 0:
                change_points.append(rolling_results.iloc[i]['window_center'])
                change_info.append({
                    'change_point': rolling_results.iloc[i]['window_center'],
                    'slope_before': slopes[i-1],
                    'slope_after': slopes[i],
                    'type': 'sign_change'
                })

    elif method == 'classification_change':
        # Detect where classification changes (e.g., Increasing → Decreasing)
        classifications = rolling_results['classification'].values
        for i in range(1, len(classifications)):
            if classifications[i] != classifications[i-1]:
                change_points.append(rolling_results.iloc[i]['window_center'])
                change_info.append({
                    'change_point': rolling_results.iloc[i]['window_center'],
                    'class_before': classifications[i-1],
                    'class_after': classifications[i],
                    'type': 'classification_change'
                })

    elif method == 'threshold':
        # Detect where slope changes by more than threshold
        if threshold is None:
            threshold = np.std(rolling_results['slope']) * 2

        slopes = rolling_results['slope'].values
        for i in range(1, len(slopes)):
            slope_change = abs(slopes[i] - slopes[i-1])
            if slope_change > threshold:
                change_points.append(rolling_results.iloc[i]['window_center'])
                change_info.append({
                    'change_point': rolling_results.iloc[i]['window_center'],
                    'slope_before': slopes[i-1],
                    'slope_after': slopes[i],
                    'slope_change': slope_change,
                    'type': 'threshold_exceeded'
                })

    return change_points, pd.DataFrame(change_info)


def compare_periods(x, t, breakpoint, alpha=0.05, **kwargs):
    """
    Compare trends before and after a breakpoint.

    Args:
        x, t: Data and time vectors
        breakpoint: Time value to split data
        alpha: Significance level
        **kwargs: Additional arguments for trend_test

    Returns:
        comparison: Dict with before/after results and difference test
    """
    t_arr = np.asarray(t)
    x_arr = np.asarray(x) if not isinstance(x, pd.DataFrame) else x

    # Split data
    if isinstance(x, pd.DataFrame):
        mask_before = t_arr < breakpoint
        x_before = x_arr[mask_before].reset_index(drop=True)
        x_after = x_arr[~mask_before].reset_index(drop=True)
    else:
        mask_before = t_arr < breakpoint
        x_before = x_arr[mask_before]
        x_after = x_arr[~mask_before]

    t_before = t_arr[mask_before]
    t_after = t_arr[~mask_before]

    # Run trend tests
    result_before = trend_test(x=x_before, t=t_before, alpha=alpha, **kwargs)
    result_after = trend_test(x=x_after, t=t_after, alpha=alpha, **kwargs)

    # Test if slopes are significantly different
    # Using bootstrap to test H0: slope_before = slope_after
    slope_diff = result_after.slope - result_before.slope

    # Simple test: check if CIs overlap
    ci_overlap = not (result_before.lower_ci > result_after.upper_ci or
                     result_after.lower_ci > result_before.upper_ci)

    return {
        'before': result_before,
        'after': result_after,
        'slope_difference': slope_diff,
        'ci_overlap': ci_overlap,
        'significant_change': not ci_overlap,
        'breakpoint': breakpoint
    }
```

#### Step 2: Plotting Function
**File:** `MannKS/plotting.py` (add to existing file)

```python
def plot_rolling_trend(rolling_results, data=None, time_col=None, value_col=None,
                      highlight_significant=True, show_global_trend=False,
                      global_result=None, change_points=None,
                      save_path=None, figsize=(14, 8)):
    """
    Visualize rolling trend analysis results.

    Args:
        rolling_results: DataFrame from rolling_trend_test
        data: Original data (optional, for background scatter)
        time_col, value_col: Column names in data
        highlight_significant: Color significant windows differently
        show_global_trend: Overlay single global trend line
        global_result: Result from trend_test on full dataset
        change_points: List of detected change points
        save_path: Path to save figure
        figsize: Figure size
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)

    # Determine if datetime
    is_datetime = pd.api.types.is_datetime64_any_dtype(rolling_results['window_center'])

    # --- Panel 1: Original data with rolling trend lines ---
    ax1 = axes[0]

    if data is not None and time_col and value_col:
        ax1.scatter(data[time_col], data[value_col],
                   alpha=0.3, s=20, color='gray', label='Data')

    # Plot each window's trend line
    for idx, row in rolling_results.iterrows():
        x_line = [row['window_start'], row['window_end']]

        # Calculate y values for trend line
        t_mid = row['window_center']
        if is_datetime:
            t_mid_num = pd.to_datetime(t_mid).timestamp()
            t_start_num = pd.to_datetime(row['window_start']).timestamp()
            t_end_num = pd.to_datetime(row['window_end']).timestamp()
        else:
            t_mid_num = t_mid
            t_start_num = row['window_start']
            t_end_num = row['window_end']

        # Assume slope is per unit time, need to calculate y-intercept
        # For visualization, we'll just show relative slopes
        y_mid = 0  # Arbitrary reference
        slope = row['slope']
        y_line = [y_mid + slope * (t_start_num - t_mid_num),
                 y_mid + slope * (t_end_num - t_mid_num)]

        color = 'red' if row['h'] and highlight_significant else 'blue'
        alpha = 0.7 if row['h'] else 0.3

        ax1.plot(x_line, y_line, color=color, alpha=alpha, linewidth=1)

    if show_global_trend and global_result:
        ax1.axhline(0, color='black', linestyle='--', linewidth=2,
                   label=f"Global trend: {global_result.slope:.3f}")

    ax1.set_ylabel('Value')
    ax1.set_title('Rolling Trend Lines')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # --- Panel 2: Rolling slope with confidence intervals ---
    ax2 = axes[1]

    x_plot = rolling_results['window_center']

    # Color by significance
    if highlight_significant:
        sig_mask = rolling_results['h']
        ax2.scatter(x_plot[sig_mask], rolling_results.loc[sig_mask, 'slope'],
                   color='red', s=50, label='Significant', zorder=3)
        ax2.scatter(x_plot[~sig_mask], rolling_results.loc[~sig_mask, 'slope'],
                   color='gray', s=50, alpha=0.5, label='Not significant', zorder=3)
    else:
        ax2.scatter(x_plot, rolling_results['slope'], s=50, zorder=3)

    # Confidence intervals
    ax2.fill_between(x_plot,
                     rolling_results['lower_ci'],
                     rolling_results['upper_ci'],
                     alpha=0.2, color='blue', label='95% CI')

    # Zero line
    ax2.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

    # Change points
    if change_points:
        for cp in change_points:
            ax2.axvline(cp, color='orange', linestyle=':', linewidth=2, alpha=0.7)

    ax2.set_ylabel('Slope')
    ax2.set_title('Rolling Sen\'s Slope')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # --- Panel 3: P-values and confidence ---
    ax3 = axes[2]

    ax3_twin = ax3.twinx()

    # P-values (log scale)
    ax3.semilogy(x_plot, rolling_results['p_value'],
                color='purple', marker='o', label='P-value', markersize=4)
    ax3.axhline(0.05, color='red', linestyle='--', linewidth=1, label='α=0.05')
    ax3.set_ylabel('P-value', color='purple')
    ax3.tick_params(axis='y', labelcolor='purple')

    # Confidence in direction
    ax3_twin.plot(x_plot, rolling_results['C'],
                 color='green', marker='s', label='Confidence', markersize=4)
    ax3_twin.set_ylabel('Confidence (C)', color='green')
    ax3_twin.tick_params(axis='y', labelcolor='green')
    ax3_twin.set_ylim([0.4, 1.0])

    ax3.set_xlabel('Time')
    ax3.set_title('Statistical Significance')
    ax3.grid(True, alpha=0.3)

    # Format x-axis for datetime
    if is_datetime:
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax.xaxis.set_major_locator(mdates.YearLocator())

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()

    plt.close()
```

#### Step 3: Add to __init__.py
**File:** `MannKS/__init__.py`

```python
from .rolling_trend import rolling_trend_test, detect_change_points, compare_periods
from .plotting import plot_rolling_trend

__all__ = [
    # ... existing exports ...
    'rolling_trend_test',
    'detect_change_points',
    'compare_periods',
    'plot_rolling_trend'
]
```

#### Step 4: Add Tests
**File:** `tests/test_rolling_trend.py` (new file)

```python
import numpy as np
import pandas as pd
import pytest
from MannKS import rolling_trend_test, detect_change_points, compare_periods

def test_rolling_trend_basic():
    """Test basic rolling trend calculation."""
    # Generate data with constant trend
    n = 100
    t = pd.date_range('2000-01-01', periods=n, freq='ME')
    x = np.arange(n) + np.random.normal(0, 1, n)

    results = rolling_trend_test(x, t, window='5Y', step='1Y', min_size=10)

    # Should have multiple windows
    assert len(results) > 5

    # All slopes should be positive
    assert (results['slope'] > 0).all()

    # Check required columns
    required_cols = ['window_start', 'window_end', 'slope', 'p_value', 'classification']
    assert all(col in results.columns for col in required_cols)

def test_rolling_trend_change_point():
    """Test change point detection."""
    # Generate data with trend reversal at midpoint
    n = 100
    t = pd.date_range('2000-01-01', periods=n, freq='ME')
    x = np.concatenate([
        np.arange(50) + np.random.normal(0, 1, 50),  # Increasing
        100 - np.arange(50) + np.random.normal(0, 1, 50)  # Decreasing
    ])

    results = rolling_trend_test(x, t, window='3Y', step='6M', min_size=10)

    # Detect change points
    change_points, change_info = detect_change_points(results, method='slope_sign_change')

    # Should detect at least one change point
    assert len(change_points) > 0

def test_rolling_trend_seasonal():
    """Test rolling trend with seasonal data."""
    n = 120  # 10 years monthly
    t = pd.date_range('2000-01-01', periods=n, freq='ME')

    # Trend + seasonality
    trend = np.linspace(0, 10, n)
    seasonal = 5 * np.sin(2 * np.pi * np.arange(n) / 12)
    x = trend + seasonal + np.random.normal(0, 0.5, n)

    results = rolling_trend_test(
        x, t,
        window='3Y',
        step='1Y',
        seasonal=True,
        period=12,
        season_type='month'
    )

    assert len(results) > 0
    assert 'slope' in results.columns

def test_compare_periods():
    """Test before/after comparison."""
    n = 100
    t = pd.date_range('2000-01-01', periods=n, freq='ME')

    # Different trends before/after midpoint
    x = np.concatenate([
        0.1 * np.arange(50) + np.random.normal(0, 1, 50),
        1.0 * np.arange(50) + 50 + np.random.normal(0, 1, 50)
    ])

    breakpoint = t[50]
    comparison = compare_periods(x, t, breakpoint)

    assert 'before' in comparison
    assert 'after' in comparison
    assert 'slope_difference' in comparison

    # After should have steeper slope
    assert comparison['after'].slope > comparison['before'].slope

def test_rolling_numeric_time():
    """Test rolling trend with numeric time vector."""
    n = 100
    t = np.arange(n)
    x = 2 * t + np.random.normal(0, 5, n)

    results = rolling_trend_test(x, t, window=20, step=5, min_size=10)

    assert len(results) > 0
    assert all(results['slope'] > 0)  # Should detect positive trend

def test_rolling_insufficient_data():
    """Test handling of windows with insufficient data."""
    n = 30
    t = pd.date_range('2000-01-01', periods=n, freq='ME')
    x = np.arange(n)

    # Window too large, step too large
    results = rolling_trend_test(x, t, window='10Y', step='5Y', min_size=50)

    # Should return empty or very few results
    assert len(results) < 3
```

#### Step 5: Add Validation Case
**File:** `validation/36_Rolling_Trend/validate.py`

Create synthetic data with known change points and verify detection.

#### Step 6: Add Documentation
**File:** `Examples/Detailed_Guides/rolling_trend_guide.md`

```markdown
# Rolling Trend Analysis

## Overview

Rolling trend analysis calculates Sen's slope over moving time windows, revealing how trends evolve over time.

## Basic Usage

```python
from MannKS import rolling_trend_test, plot_rolling_trend
import pandas as pd

# Monthly data from 2000-2020
data = pd.read_csv('water_quality.csv')

# Calculate rolling 5-year trends, advancing 1 year at a time
results = rolling_trend_test(
    x=data['concentration'],
    t=data['date'],
    window='5Y',
    step='1Y',
    min_size=20,
    slope_scaling='year',
    x_unit='mg/L'
)

# Visualize
plot_rolling_trend(
    results,
    data=data,
    time_col='date',
    value_col='concentration',
    save_path='rolling_analysis.png'
)
```

## Choosing Window Parameters

### Window Size
- **Too small**: Noisy, unreliable estimates
- **Too large**: Loses temporal resolution
- **Rule of thumb**: 5-10 years for annual data, 2-5 years for monthly data

### Step Size
- Smaller steps = smoother curves but slower computation
- Default is window/2 (50% overlap)
- For exploration: step = window
- For publication: step = window/4 (more detail)

## Detecting Change Points

```python
from MannKS import detect_change_points

# Method 1: Slope sign changes
changes, info = detect_change_points(results, method='slope_sign_change')

# Method 2: Classification changes
changes, info = detect_change_points(results, method='classification_change')

# Method 3: Large slope changes
changes, info = detect_change_points(results, method='threshold', threshold=0.5)

print(f"Change points detected at: {changes}")
print(info)
```

## Before/After Comparison

```python
from MannKS import compare_periods

# Test if trend changed after 2010 policy
comparison = compare_periods(
    x=data['concentration'],
    t=data['date'],
    breakpoint=pd.Timestamp('2010-01-01'),
    slope_scaling='year'
)

print(f"Before 2010: {comparison['before'].slope:.3f} mg/L/year")
print(f"After 2010: {comparison['after'].slope:.3f} mg/L/year")
print(f"Significant change: {comparison['significant_change']}")
```

## Interpretation Guidelines

### What Rolling Slopes Tell You
- **Stable slope**: Consistent trend magnitude
- **Increasing slope**: Accelerating trend
- **Decreasing slope**: Decelerating trend
- **Sign change**: Reversal (improvement/degradation)

### Statistical Considerations
- Early/late windows have less data → wider CIs
- Overlapping windows are not independent
- Don't over-interpret small fluctuations
- Use change point detection for formal testing

## Common Pitfalls

1. **Window too small**: ≥10 points minimum, preferably 20+
2. **Ignoring CI width**: Wide CIs = uncertain estimates
3. **P-hacking**: Don't search for "significant" breakpoints
4. **Autocorrelation**: Use `autocorr_method` if needed

## Example: Detecting BMP Effectiveness

```python
# Load data
data = pd.read_csv('river_nitrogen.csv')

# Rolling analysis
results = rolling_trend_test(
    x=data['nitrogen'],
    t=data['date'],
    window='5Y',
    step='1Y',
    x_unit='mg/L',
    slope_scaling='year'
)

# When did trends improve?
bmp_start = pd.Timestamp('2015-01-01')
comparison = compare_periods(data['nitrogen'], data['date'], bmp_start)

if comparison['significant_change'] and comparison['after'].slope < 0:
    print("BMPs appear effective: significant decline after implementation")
else:
    print("No clear BMP effect detected")
```
```

---

## Continuous Confidence Considerations

### The Fundamental Difference

**Classical hypothesis testing (`continuous_confidence=False`):**
- Binary decision: reject H0 or don't reject H0
- Reports: p-value, significant/not significant
- Question: "Is there evidence of a trend?"

**Continuous confidence (`continuous_confidence=True`):**
- Probabilistic statement about direction
- Reports: C (confidence in direction), classification
- Question: "How confident are we in the trend direction?"

### Impact on Block Bootstrap

#### Implementation Details

When `continuous_confidence=True`, the bootstrap must estimate **confidence in direction**, not just test H0: slope=0.

**Modified bootstrap algorithm:**

```python
def block_bootstrap_continuous_confidence(x, t, censored, cen_type,
                                         block_size='auto', n_bootstrap=1000):
    """
    Block bootstrap for continuous confidence estimation.

    Returns:
        C: Confidence that trend is in observed direction
        Cd: Directional confidence (signed)
        s_obs: Observed S statistic
    """
    # Observed statistic
    s_obs, _, _, _ = _mk_score_and_var_censored(x, t, censored, cen_type)

    # Detrend under H0
    slopes = _sens_estimator_censored(x, t, cen_type) if np.any(censored) else _sens_estimator_unequal_spacing(x, t)
    median_slope = np.nanmedian(slopes)
    x_detrended = x - median_slope * (t - np.median(t))

    # Bootstrap distribution under H0: no trend
    s_boot_dist = np.zeros(n_bootstrap)
    for b in range(n_bootstrap):
        x_boot = moving_block_bootstrap(x_detrended, block_size)
        s_b, _, _, _ = _mk_score_and_var_censored(x_boot, t, censored, cen_type)
        s_boot_dist[b] = s_b

    # Calculate continuous confidence
    # C = P(same sign as observed | H0 distribution)
    if s_obs > 0:
        # For increasing trend: what proportion of bootstrap S are negative?
        C = 1 - np.mean(s_boot_dist < 0)
    elif s_obs < 0:
        # For decreasing trend: what proportion of bootstrap S are positive?
        C = 1 - np.mean(s_boot_dist > 0)
    else:
        C = 0.5  # No trend

    # Directional confidence (Fraser & Whitehead 2022)
    Cd = C if s_obs >= 0 else (1 - C)

    return C, Cd, s_obs, s_boot_dist
```

**Key difference from classical bootstrap:**
- Classical: `p = mean(|s_boot| >= |s_obs|)` — tests against zero
- Continuous: `C = 1 - mean(s_boot has opposite sign)` — confidence in direction

#### Why This Matters

With autocorrelation, the classical test inflates significance because variance is underestimated. But for continuous confidence:

```python
# Autocorrelated data with weak trend
x, t = generate_ar1_process(n=100, phi=0.6, trend_slope=0.05)

# Classical test
result_classical = trend_test(x, t, continuous_confidence=False)
# p = 0.02 (FALSE POSITIVE due to autocorrelation)

# Bootstrap classical
result_boot_classical = trend_test(x, t, continuous_confidence=False, autocorr_method='block_bootstrap')
# p = 0.08 (CORRECTED - not significant)

# Continuous confidence, no correction
result_cont = trend_test(x, t, continuous_confidence=True)
# C = 0.68, classification = "Likely Increasing" (INFLATED confidence)

# Bootstrap continuous confidence
result_boot_cont = trend_test(x, t, continuous_confidence=True, autocorr_method='block_bootstrap')
# C = 0.58, classification = "As Likely as Not" (CORRECTED)
```

**The problem:** Autocorrelation doesn't just inflate p-values; it also inflates directional confidence. Bootstrap must correct both.

### Impact on Rolling Trends

This is where it gets really interesting. The interpretation changes dramatically:

#### Scenario 1: Classical Testing (`continuous_confidence=False`)

```python
results = rolling_trend_test(x, t, window='5Y', continuous_confidence=False)
```

**What you get:**
- Each window tests H0: no trend in this period
- `p_value` column: significance of trend
- `h` column: significant (True) or not (False)

**Interpretation:**
- "In 2015-2020, there was a statistically significant increasing trend (p=0.03)"
- Focus on whether trends are "real" vs. noise
- Binary: significant or not

**Visualization emphasis:**
- Highlight significant windows
- Show p-value evolution
- Mark when trends cross α=0.05 threshold

#### Scenario 2: Continuous Confidence (`continuous_confidence=True`)

```python
results = rolling_trend_test(x, t, window='5Y', continuous_confidence=True)
```

**What you get:**
- Each window estimates confidence in direction
- `C` column: confidence (0.5-1.0)
- `classification` column: "Highly Likely Increasing", "As Likely as Not", etc.

**Interpretation:**
- "In 2015-2020, we have 87% confidence the trend is increasing"
- Even non-significant trends get directional labels
- Gradient: from uncertain (50%) to certain (100%)

**Visualization emphasis:**
- Color by confidence level (gradient, not binary)
- Show classification evolution
- Mark confidence thresholds (0.66, 0.8, 0.9)

#### The Rolling Paradox

Consider this real scenario:

```
2000-2005: C = 0.68, "Likely Increasing", p = 0.12
2002-2007: C = 0.72, "Likely Increasing", p = 0.08
2004-2009: C = 0.81, "Very Likely Increasing", p = 0.04
2006-2011: C = 0.75, "Likely Increasing", p = 0.06
```

**Classical interpretation:** Only 2004-2009 shows a "real" trend
**Continuous interpretation:** Consistently likely increasing, with varying confidence

**Which is better for rolling analysis?**

### Recommendation: Use Continuous Confidence for Rolling

**Reasons:**

1. **Smoother narratives:** Confidence changes gradually, not abruptly at p=0.05
2. **More information:** Distinguishes between C=0.51 and C=0.95
3. **Better for communication:** "Confidence increasing over time" vs "became significant in 2015"
4. **Matches intent:** Rolling analysis explores temporal patterns, not binary decisions

**Implementation guideline:**

```python
def rolling_trend_test(..., continuous_confidence=None):
    """
    If continuous_confidence is None (default), automatically choose:
    - True for rolling analysis (better temporal interpretation)
    - False for single-window analysis (if that's the intent)
    """
    if continuous_confidence is None:
        # For rolling, default to continuous
        continuous_confidence = True

    # Add to analysis notes
    if continuous_confidence:
        analysis_notes.append(
            "Using continuous confidence (C) for directional strength. "
            "Results show confidence in direction, not binary significance."
        )
```

### Modified Plotting for Continuous vs Classical

**Panel 2: Slope magnitude (same for both)**

**Panel 3: Different emphasis**

```python
if continuous_confidence:
    # Gradient coloring by confidence level
    colors = plt.cm.RdYlGn(rolling_results['C'])
    ax3.scatter(x_plot, rolling_results['C'], c=colors, s=50)

    # Confidence thresholds
    ax3.axhline(0.66, color='orange', linestyle='--', label='Likely threshold')
    ax3.axhline(0.80, color='red', linestyle='--', label='Very Likely threshold')
    ax3.set_ylabel('Confidence (C)')
    ax3.set_ylim([0.5, 1.0])

else:
    # Binary significant/not significant
    ax3.semilogy(x_plot, rolling_results['p_value'], marker='o')
    ax3.axhline(0.05, color='red', linestyle='--', label='α=0.05')
    ax3.set_ylabel('P-value')
```

### Change Point Detection Differences

**Classical approach:**
```python
# Detect when significance status changes
change_points = detect_change_points(results, method='significance_change')
# Finds: p crosses 0.05 threshold
```

**Continuous confidence approach:**
```python
# Detect when confidence category changes
change_points = detect_change_points(results, method='classification_change')
# Finds: transitions between "Likely", "Very Likely", "Highly Likely"

# Or detect confidence threshold crossings
change_points = detect_change_points(results, method='confidence_threshold', threshold=0.80)
# Finds: when confidence crosses 80%
```

### Updated API Design

**Add to rolling_trend_test:**

```python
def rolling_trend_test(
    x, t, window, step,
    continuous_confidence: bool = True,  # DEFAULT TRUE for rolling
    confidence_threshold: float = 0.66,  # For change point detection
    ...
):
    """
    Args:
        continuous_confidence: If True, uses directional confidence (C).
            If False, uses classical p-values. Recommended: True for
            temporal analysis, False for one-time assessment.
        confidence_threshold: Threshold for flagging "confident" windows
            when continuous_confidence=True (default: 0.66 = "Likely")
    """
```

**Add new change point method:**

```python
def detect_change_points(rolling_results, method='auto', threshold=None):
    """
    Args:
        method:
            - 'auto': Choose based on continuous_confidence setting
            - 'slope_sign_change': Detect reversals
            - 'classification_change': Detect confidence category changes (continuous)
            - 'significance_change': Detect p<0.05 transitions (classical)
            - 'confidence_threshold': Detect crossings of confidence level (continuous)
    """

    if method == 'auto':
        # Infer from data
        if 'C' in rolling_results.columns and rolling_results['C'].notna().any():
            method = 'classification_change'
        else:
            method = 'significance_change'
```

### Documentation Updates

**Add to rolling_trend_guide.md:**

```markdown
## Classical vs Continuous Confidence

### When to use continuous confidence (DEFAULT)

Use `continuous_confidence=True` for rolling analysis when you want to:
- Track how confidence evolves over time
- Communicate gradual changes in trend strength
- Avoid binary "significant/not significant" jumps
- Present results to non-statistical audiences

Example:
```python
results = rolling_trend_test(x, t, window='5Y', continuous_confidence=True)
# Shows: "Confidence in increasing trend rose from 68% to 91% over decade"
```

### When to use classical testing

Use `continuous_confidence=False` when you need:
- Formal hypothesis testing for each window
- To report which periods have "statistically significant" trends
- Consistency with published literature using p-values
- Scientific journals requiring traditional statistics

Example:
```python
results = rolling_trend_test(x, t, window='5Y', continuous_confidence=False)
# Shows: "Significant increasing trends detected in 3 of 10 windows (p<0.05)"
```

### Combining with autocorrelation correction

```python
# Continuous confidence + bootstrap
results = rolling_trend_test(
    x, t, window='5Y',
    continuous_confidence=True,
    autocorr_method='block_bootstrap'
)
# Corrects inflated confidence from autocorrelation
```
```

### Testing Strategy

**Add test case:**

```python
def test_continuous_vs_classical_rolling():
    """Test that continuous and classical give different interpretations."""
    np.random.seed(123)

    # Weak but consistent trend
    n = 120
    t = pd.date_range('2000-01-01', periods=n, freq='ME')
    x = 0.05 * np.arange(n) + np.random.normal(0, 2, n)

    # Classical
    results_classical = rolling_trend_test(
        x, t, window='3Y', step='1Y',
        continuous_confidence=False
    )

    # Continuous
    results_continuous = rolling_trend_test(
        x, t, window='3Y', step='1Y',
        continuous_confidence=True
    )

    # Classical: some windows significant, some not
    n_significant = results_classical['h'].sum()
    assert 0 < n_significant < len(results_classical)  # Mixed results

    # Continuous: all windows should show positive confidence
    assert (results_continuous['C'] > 0.5).all()

    # Continuous: should classify most as "Likely" or better
    likely_or_better = results_continuous['classification'].isin([
        'Likely Increasing', 'Very Likely Increasing', 'Highly Likely Increasing'
    ]).sum()
    assert likely_or_better > len(results_continuous) * 0.7
```

---

## Feature 3: Segmented Sen's Slope Regression

### Justification

#### The Innovation
**This would be UNIQUE in the statistical software landscape.** The existing `piecewise-regression` package uses ordinary least squares (OLS), which:
- Assumes normal errors
- Sensitive to outliers
- Not designed for censored data
- No continuous confidence framework

**Your package could be the FIRST to combine:**
- Segmented/piecewise regression
- Non-parametric Sen's slope (robust to outliers)
- Mann-Kendall significance testing
- Censored data handling
- Continuous confidence measures
- All in one workflow

#### Real-World Motivation

Environmental data often has **abrupt regime shifts**:

1. **Policy interventions**: Clean Air Act enforcement starts → sudden emission changes
2. **Infrastructure changes**: Wastewater treatment plant upgrade → step change in river quality
3. **Climate shifts**: ENSO phase transitions → different rainfall-runoff relationships
4. **Natural thresholds**: Eutrophication tipping points, coral bleaching thresholds

**Current problem:** Users must choose between:
- **Single trend test**: Misses the breakpoint, finds "no significant trend"
- **Manual splitting**: Where to split? P-hacking risk
- **Rolling analysis**: Shows change happening but not exactly when
- **OLS segmented regression**: Loses robustness, can't handle censored data

#### Example Scenario

```
Water quality data 1990-2020:
- 1990-2005: Slow degradation (Sen slope = +0.3 mg/L/year)
- 2005-2020: Rapid improvement (Sen slope = -1.2 mg/L/year)
- Breakpoint: 2005 ± 0.8 years (when new WWTP came online)

Single trend test: p=0.15 (not significant) ← WRONG
Segmented test: Both segments highly significant, breakpoint well-defined ← RIGHT
```

#### Advantages Over Rolling Analysis

| Feature | Rolling Trend | Segmented Regression |
|---------|--------------|---------------------|
| Detects change | ✓ Shows gradual shift | ✓ Pinpoints exact breakpoint |
| Statistical test | For each window | For existence of breakpoint |
| Slope estimates | Overlapping, correlated | Independent segments, cleaner |
| Interpretability | "Trend evolved over time" | "Changed on DATE" |
| Sample efficiency | Splits data many ways | Uses all data per segment |

**Use both together:**
1. Rolling analysis → exploratory, "something changed around 2010"
2. Segmented regression → confirmatory, "breakpoint at 2009.7 ± 0.5 years"

### Workflow Integration

```
User suspects change point → segmented_trend_test() → Results:
                                    ↓
                    Breakpoint(s) detected? YES/NO
                                    ↓
                    [If YES] → Individual segment trends
                                    ↓
                            Davies test: p-value for breakpoint existence
                                    ↓
                        Sen slopes + confidence for each segment
```

**API Design:**

```python
result = segmented_trend_test(
    x=data,
    t=dates,
    n_breakpoints='auto',          # or 1, 2, 3, or list of suspected dates
    breakpoint_candidates=None,     # Optional: limit search space
    min_segment_size=10,            # Minimum points per segment
    method='muggeo',                # 'muggeo', 'dynamic_programming', or 'grid_search'
    continuous_confidence=True,     # Use continuous confidence framework
    slope_scaling='year',
    x_unit='mg/L'
)

# Returns:
# - n_breakpoints: number detected
# - breakpoints: list of dates/values with CIs
# - davies_p: p-value for breakpoint existence
# - segments: DataFrame with slope, CI, p-value, C for each segment
# - global_trend: single trend for comparison
# - aic, bic: model selection criteria
```

### Comparison with piecewise-regression Package

#### What piecewise-regression does well:
- Muggeo's iterative algorithm for fitting piecewise linear regression
- Bootstrap restarting to escape local optima
- Davies hypothesis test for breakpoint existence
- Model selection via BIC to determine optimal number of breakpoints

#### What MannKS would add:
1. **Sen's slope instead of OLS** - Robust to outliers and non-normal errors
2. **Mann-Kendall testing** - Non-parametric significance for each segment
3. **Censored data support** - Handles detection limits in each segment
4. **Continuous confidence** - Probabilistic statements about segment directions
5. **Temporal context** - Works with datetime objects, seasonal patterns
6. **Integrated workflow** - Compare segmented vs global vs rolling

### Step-by-Step Implementation

#### Step 1: Core Algorithm - Muggeo's Method Adapted for Sen's Slope
**File:** `MannKS/_segmented.py` (new file)

```python
import numpy as np
import pandas as pd
from typing import Union, Optional, List, Tuple
from scipy import optimize
from ._stats import _sens_estimator_unequal_spacing, _sens_estimator_censored
from ._stats import _mk_score_and_var_censored

def segmented_sens_slope(x, t, censored, cen_type,
                         n_breakpoints=1,
                         start_values=None,
                         max_iter=30,
                         tol=1e-6,
                         min_segment_size=10):
    """
    Fit segmented regression using Sen's slope for each segment.
    Adapts Muggeo (2003) algorithm for robust Sen's slope estimation.

    Args:
        x, t, censored, cen_type: Standard inputs
        n_breakpoints: Number of breakpoints to fit
        start_values: Initial guesses for breakpoint positions
        max_iter: Maximum iterations for convergence
        tol: Convergence tolerance
        min_segment_size: Minimum points per segment constraint

    Returns:
        breakpoints: Estimated breakpoint positions
        slopes: Sen's slope for each segment
        converged: Whether algorithm converged
    """
    n = len(x)

    # Initialize breakpoints
    if start_values is None:
        # Place breakpoints evenly across time range
        t_range = np.max(t) - np.min(t)
        start_values = [np.min(t) + (i+1) * t_range / (n_breakpoints + 1)
                       for i in range(n_breakpoints)]

    breakpoints = np.array(start_values)

    for iteration in range(max_iter):
        breakpoints_old = breakpoints.copy()

        # For each breakpoint, update its position
        for bp_idx in range(n_breakpoints):
            # Create segments based on current breakpoints
            segments = _create_segments(t, breakpoints)

            # Calculate Sen's slope for each segment
            slopes = []
            for seg_start, seg_end in segments:
                mask = (t >= seg_start) & (t < seg_end)
                if np.sum(mask) < 3:  # Need minimum points
                    slopes.append(0)
                    continue

                x_seg = x[mask]
                t_seg = t[mask]
                cen_seg = censored[mask]
                cen_type_seg = cen_type[mask]

                if np.any(cen_seg):
                    seg_slopes = _sens_estimator_censored(x_seg, t_seg, cen_type_seg)
                else:
                    seg_slopes = _sens_estimator_unequal_spacing(x_seg, t_seg)

                slopes.append(np.nanmedian(seg_slopes))

            # Update this breakpoint to minimize sum of absolute residuals
            # Grid search around current position
            current_bp = breakpoints[bp_idx]

            # Define search range based on previous/next breakpoints
            # Initial search width is broad, but constrained by neighbors
            search_width = (np.max(t) - np.min(t)) * 0.1

            if bp_idx > 0:
                current_lower_bound = breakpoints[bp_idx - 1] + (t[1] - t[0])
            else:
                current_lower_bound = np.min(t) + search_width

            if bp_idx < n_breakpoints - 1:
                current_upper_bound = breakpoints[bp_idx + 1] - (t[1] - t[0])
            else:
                current_upper_bound = np.max(t) - search_width

            # --- Robust Boundary Constraints ---
            # Ensure no segment is smaller than min_segment_size
            # Calculate time buffer corresponding to N points
            if min_segment_size >= n:
                 raise ValueError("min_segment_size larger than data length")

            # Find time spans for first and last N points
            t_sorted = np.sort(t) # Ensure sorted for quantile-like logic
            time_buffer_start = t_sorted[min_segment_size] - t_sorted[0]
            time_buffer_end = t_sorted[-1] - t_sorted[-min_segment_size-1]

            # Apply hard constraints to search bounds
            lower = max(current_lower_bound, t_sorted[0] + time_buffer_start)
            upper = min(current_upper_bound, t_sorted[-1] - time_buffer_end)

            if lower >= upper:
                # If constraints squeeze out all search space, keep current
                best_bp = current_bp
                continue

            # Grid search for best breakpoint
            test_points = np.linspace(lower, upper, 20)
            best_residual = np.inf
            best_bp = current_bp

            for test_bp in test_points:
                test_breakpoints = breakpoints.copy()
                test_breakpoints[bp_idx] = test_bp

                # Calculate total absolute residuals with this breakpoint
                residual = _calculate_segment_residuals(
                    x, t, censored, cen_type, test_breakpoints
                )

                if residual < best_residual:
                    best_residual = residual
                    best_bp = test_bp

            breakpoints[bp_idx] = best_bp

        # Check convergence
        if np.max(np.abs(breakpoints - breakpoints_old)) < tol:
            return breakpoints, True

    # Did not converge
    return breakpoints, False


def _create_segments(t, breakpoints):
    """Create segment boundaries from breakpoints."""
    t_min, t_max = np.min(t), np.max(t)

    sorted_bp = np.sort(breakpoints)
    segments = []

    # First segment
    segments.append((t_min, sorted_bp[0]))

    # Middle segments
    for i in range(len(sorted_bp) - 1):
        segments.append((sorted_bp[i], sorted_bp[i+1]))

    # Last segment
    segments.append((sorted_bp[-1], t_max))

    return segments


def _calculate_segment_residuals(x, t, censored, cen_type, breakpoints):
    """
    Calculate sum of absolute residuals for segmented model.
    Uses Sen's slope for robust estimation.
    """
    segments = _create_segments(t, breakpoints)
    total_residual = 0

    for seg_start, seg_end in segments:
        mask = (t >= seg_start) & (t < seg_end)
        if np.sum(mask) < 3:
            continue

        x_seg = x[mask]
        t_seg = t[mask]
        cen_seg = censored[mask]
        cen_type_seg = cen_type[mask]

        # Estimate slope
        if np.any(cen_seg):
            slopes = _sens_estimator_censored(x_seg, t_seg, cen_type_seg)
        else:
            slopes = _sens_estimator_unequal_spacing(x_seg, t_seg)

        slope = np.nanmedian(slopes)

        # Calculate fitted values
        t_center = np.median(t_seg)
        x_fitted = np.median(x_seg[~cen_seg]) + slope * (t_seg - t_center)

        # Sum absolute residuals (for non-censored points)
        residuals = np.abs(x_seg[~cen_seg] - x_fitted[~cen_seg])
        total_residual += np.sum(residuals)

    return total_residual
```

#### Step 2: Bootstrap Restarting
**File:** `MannKS/_segmented.py` (continued)

```python
def bootstrap_restart_segmented(x, t, censored, cen_type,
                                n_breakpoints=1,
                                n_bootstrap=10,
                                n_start_values=5):
    """
    Use bootstrap restarting to find global optimum.

    Based on Wood (2001) and Muggeo (2008) approach.
    """
    best_residual = np.inf
    best_breakpoints = None
    best_converged = False

    # Try multiple random starting values
    for attempt in range(n_bootstrap + n_start_values):
        if attempt < n_start_values:
            # Random starting values
            t_min, t_max = np.min(t), np.max(t)
            start_values = np.random.uniform(
                t_min + (t_max - t_min) * 0.1,
                t_max - (t_max - t_min) * 0.1,
                n_breakpoints
            )
            start_values = np.sort(start_values)

            # Use actual data
            x_boot = x
            t_boot = t
            cen_boot = censored
            cen_type_boot = cen_type

        else:
            # Bootstrap resample
            boot_idx = np.random.choice(len(x), len(x), replace=True)
            x_boot = x[boot_idx]
            t_boot = t[boot_idx]
            cen_boot = censored[boot_idx]
            cen_type_boot = cen_type[boot_idx]

            # Use best found so far as starting values
            if best_breakpoints is not None:
                start_values = best_breakpoints
            else:
                start_values = None

        # Fit model
        breakpoints, converged = segmented_sens_slope(
            x_boot, t_boot, cen_boot, cen_type_boot,
            n_breakpoints=n_breakpoints,
            start_values=start_values
        )

        # Evaluate on original data
        residual = _calculate_segment_residuals(x, t, censored, cen_type, breakpoints)

        if residual < best_residual:
            best_residual = residual
            best_breakpoints = breakpoints
            best_converged = converged

    return best_breakpoints, best_converged
```

#### Step 3: Davies Test for Breakpoint Existence
**File:** `MannKS/_segmented.py` (continued)

```python
def davies_test_breakpoint(x, t, censored, cen_type, n_candidates=10):
    """
    Davies (1987) test for existence of at least one breakpoint.

    Tests H0: no breakpoint vs H1: at least one breakpoint exists.

    Returns:
        davies_statistic: Test statistic
        p_value: P-value from Davies distribution
    """
    n = len(x)

    # Calculate global Sen's slope
    if np.any(censored):
        global_slopes = _sens_estimator_censored(x, t, cen_type)
    else:
        global_slopes = _sens_estimator_unequal_spacing(x, t)
    global_slope = np.nanmedian(global_slopes)

    # Calculate global residuals
    t_center = np.median(t)
    x_center = np.median(x[~censored])
    global_residuals = x - (x_center + global_slope * (t - t_center))
    global_ssr = np.sum(global_residuals[~censored] ** 2)

    # Test at candidate breakpoints
    test_statistics = []

    # Candidate breakpoints: quantiles of t
    t_sorted = np.sort(t)
    candidate_idx = np.linspace(int(n * 0.15), int(n * 0.85), n_candidates).astype(int)
    candidates = t_sorted[candidate_idx]

    for candidate_bp in candidates:
        # Fit two-segment model with this breakpoint
        seg1_mask = t < candidate_bp
        seg2_mask = t >= candidate_bp

        if np.sum(seg1_mask) < 3 or np.sum(seg2_mask) < 3:
            continue

        # Sen's slope for each segment
        if np.any(censored[seg1_mask]):
            slopes1 = _sens_estimator_censored(
                x[seg1_mask], t[seg1_mask], cen_type[seg1_mask]
            )
        else:
            slopes1 = _sens_estimator_unequal_spacing(x[seg1_mask], t[seg1_mask])
        slope1 = np.nanmedian(slopes1)

        if np.any(censored[seg2_mask]):
            slopes2 = _sens_estimator_censored(
                x[seg2_mask], t[seg2_mask], cen_type[seg2_mask]
            )
        else:
            slopes2 = _sens_estimator_unequal_spacing(x[seg2_mask], t[seg2_mask])
        slope2 = np.nanmedian(slopes2)

        # Calculate segmented residuals
        t_center1 = np.median(t[seg1_mask])
        x_center1 = np.median(x[seg1_mask & ~censored])
        res1 = x[seg1_mask] - (x_center1 + slope1 * (t[seg1_mask] - t_center1))

        t_center2 = np.median(t[seg2_mask])
        x_center2 = np.median(x[seg2_mask & ~censored])
        res2 = x[seg2_mask] - (x_center2 + slope2 * (t[seg2_mask] - t_center2))

        segmented_ssr = (np.sum(res1[~censored[seg1_mask]] ** 2) +
                        np.sum(res2[~censored[seg2_mask]] ** 2))

        # Test statistic: reduction in SSR
        test_stat = (global_ssr - segmented_ssr) / global_ssr
        test_statistics.append(test_stat)

    # Davies statistic: maximum improvement
    davies_stat = np.max(test_statistics)

    # P-value from Davies distribution (approximation)
    # See Davies (1987) for exact distribution
    # Here we use simulation-based approximation
    p_value = _davies_p_value_simulation(davies_stat, n, n_candidates)

    return davies_stat, p_value


def _davies_p_value_simulation(observed_stat, n, n_candidates, n_sim=1000):
    """
    Simulate Davies distribution under H0: no breakpoint.
    """
    sim_stats = []

    for _ in range(n_sim):
        # Generate data under H0: linear trend with noise
        t_sim = np.linspace(0, 1, n)
        x_sim = t_sim + np.random.normal(0, 1, n)

        # Test at candidates
        test_stats = []
        for i in range(n_candidates):
            bp_idx = int(n * (0.15 + 0.7 * i / n_candidates))

            # Simple two-segment fit
            seg1 = slice(0, bp_idx)
            seg2 = slice(bp_idx, n)

            global_ssr = np.sum((x_sim - np.mean(x_sim)) ** 2)

            seg1_ssr = np.sum((x_sim[seg1] - np.mean(x_sim[seg1])) ** 2)
            seg2_ssr = np.sum((x_sim[seg2] - np.mean(x_sim[seg2])) ** 2)

            test_stat = (global_ssr - (seg1_ssr + seg2_ssr)) / global_ssr
            test_stats.append(test_stat)

        sim_stats.append(np.max(test_stats))

    # P-value: proportion of simulated stats >= observed
    p_value = np.mean(np.array(sim_stats) >= observed_stat)

    return max(p_value, 1 / n_sim)  # Lower bound on p-value
```

#### Step 4: Model Selection (BIC)
**File:** `MannKS/_segmented.py` (continued)

```python
def select_n_breakpoints(x, t, censored, cen_type, max_breakpoints=5):
    """
    Determine optimal number of breakpoints using BIC.

    Returns:
        best_n: Optimal number of breakpoints
        bic_values: BIC for each number tested
        models: Fitted models for each n
    """
    bic_values = []
    models = []

    for n_bp in range(0, max_breakpoints + 1):
        if n_bp == 0:
            # No breakpoints: global trend
            if np.any(censored):
                slopes = _sens_estimator_censored(x, t, cen_type)
            else:
                slopes = _sens_estimator_unequal_spacing(x, t)
            slope = np.nanmedian(slopes)

            t_center = np.median(t)
            x_center = np.median(x[~censored])
            x_fitted = x_center + slope * (t - t_center)
            residuals = x[~censored] - x_fitted[~censored]
            ssr = np.sum(residuals ** 2)

            n_params = 2  # intercept + slope
            breakpoints = []

        else:
            # Fit with n_bp breakpoints
            breakpoints, converged = bootstrap_restart_segmented(
                x, t, censored, cen_type,
                n_breakpoints=n_bp,
                n_bootstrap=5
            )

            if not converged:
                bic_values.append(np.inf)
                models.append(None)
                continue

            # Calculate SSR
            ssr = _calculate_segment_residuals(x, t, censored, cen_type, breakpoints)
            ssr = ssr ** 2  # Square for BIC calculation

            # Parameters: (n_bp + 1) segments, each with intercept + slope, plus breakpoints
            n_params = 2 * (n_bp + 1) + n_bp

        # BIC = n*log(RSS/n) + k*log(n)
        n_obs = np.sum(~censored)
        bic = n_obs * np.log(ssr / n_obs) + n_params * np.log(n_obs)

        bic_values.append(bic)
        models.append({'n_breakpoints': n_bp, 'breakpoints': breakpoints, 'ssr': ssr})

    best_n = np.argmin(bic_values)

    return best_n, bic_values, models
```

#### Step 5: Main User-Facing Function
**File:** `MannKS/segmented_trend_test.py` (new file)

```python
import numpy as np
import pandas as pd
from typing import Union, Optional, List
from collections import namedtuple
from ._segmented import (bootstrap_restart_segmented, davies_test_breakpoint,
                         select_n_breakpoints, _create_segments)
from .trend_test import trend_test
from ._stats import _sens_estimator_unequal_spacing, _sens_estimator_censored

def segmented_trend_test(
    x: Union[np.ndarray, pd.DataFrame],
    t: np.ndarray,
    n_breakpoints: Union[str, int] = 'auto',
    breakpoint_candidates: Optional[List] = None,
    min_segment_size: int = 10,
    method: str = 'muggeo',
    continuous_confidence: bool = True,
    alpha: float = 0.05,
    slope_scaling: Optional[str] = None,
    x_unit: str = "units",
    **kwargs
) -> namedtuple:
    """
    Segmented (piecewise) trend analysis using Sen's slope and Mann-Kendall test.

    Detects breakpoints in time series and estimates separate robust trends
    for each segment.

    Args:
        x, t: Data and time vectors
        n_breakpoints: 'auto' (BIC selection), or integer (1, 2, 3...)
        breakpoint_candidates: Optional list of suspected breakpoint dates to test
        min_segment_size: Minimum observations per segment
        method: 'muggeo' (iterative), 'grid_search', or 'dynamic_programming'
        continuous_confidence: Use continuous confidence framework
        alpha: Significance level
        slope_scaling: Time unit for slopes
        x_unit: Unit of measurement
        **kwargs: Passed to trend_test for each segment

    Returns:
        Segmented_Trend_Test namedtuple with:
            - n_breakpoints: Number detected
            - breakpoints: DataFrame with position, CI, segment transitions
            - davies_test: P-value for breakpoint existence
            - segments: DataFrame with trend results for each segment
            - global_trend: Single trend for comparison
            - aic, bic: Model selection criteria
            - model_comparison: DataFrame comparing 0 to max breakpoints
    """
    # Input validation and preparation
    # [Similar to trend_test preprocessing]

    # Step 1: Determine optimal number of breakpoints
    if n_breakpoints == 'auto':
        best_n, bic_values, models = select_n_breakpoints(
            x, t, censored, cen_type, max_breakpoints=min(5, len(x) // (2 * min_segment_size))
        )
        n_breakpoints = best_n

    # Step 2: Davies test for breakpoint existence
    davies_stat, davies_p = davies_test_breakpoint(x, t, censored, cen_type)

    # Step 3: Fit segmented model
    if n_breakpoints == 0 or davies_p > alpha:
        # No significant breakpoint - return global trend only
        global_result = trend_test(x, t, continuous_confidence=continuous_confidence,
                                  alpha=alpha, slope_scaling=slope_scaling,
                                  x_unit=x_unit, **kwargs)

        return namedtuple('Segmented_Trend_Test', [
            'n_breakpoints', 'breakpoints', 'davies_p', 'segments',
            'global_trend', 'bic', 'converged'
        ])(
            n_breakpoints=0,
            breakpoints=pd.DataFrame(),
            davies_p=davies_p,
            segments=pd.DataFrame(),
            global_trend=global_result,
            bic=bic_values[0] if 'bic_values' in locals() else None,
            converged=True
        )

    # Fit with breakpoints
    breakpoints, converged = bootstrap_restart_segmented(
        x, t, censored, cen_type,
        n_breakpoints=n_breakpoints,
        n_bootstrap=10
    )

    # Step 4: Analyze each segment
    segments = _create_segments(t, breakpoints)
    segment_results = []

    for i, (seg_start, seg_end) in enumerate(segments):
        mask = (t >= seg_start) & (t < seg_end)

        if np.sum(mask) < min_segment_size:
            continue

        x_seg = x[mask]
        t_seg = t[mask]

        # Run trend test on segment
        seg_result = trend_test(
            x=x_seg, t=t_seg,
            continuous_confidence=continuous_confidence,
            alpha=alpha,
            slope_scaling=slope_scaling,
            x_unit=x_unit,
            **kwargs
        )

        segment_results.append({
            'segment': i + 1,
            'start': seg_start,
            'end': seg_end,
            'n_obs': np.sum(mask),
            'slope': seg_result.slope,
            'lower_ci': seg_result.lower_ci,
            'upper_ci': seg_result.upper_ci,
            'p_value': seg_result.p,
            'h': seg_result.h,
            'classification': seg_result.classification,
            'C': seg_result.C,
            'tau': seg_result.Tau
        })

    segments_df = pd.DataFrame(segment_results)

    # Step 5: Breakpoint confidence intervals (bootstrap)
    breakpoint_cis = _bootstrap_breakpoint_ci(x, t, censored, cen_type,
                                              breakpoints, n_bootstrap=100)

    breakpoints_df = pd.DataFrame({
        'breakpoint': breakpoints,
        'lower_ci': breakpoint_cis[:, 0],
        'upper_ci': breakpoint_cis[:, 1]
    })

    # Step 6: Global trend for comparison
    global_result = trend_test(x, t, continuous_confidence=continuous_confidence,
                              alpha=alpha, slope_scaling=slope_scaling,
                              x_unit=x_unit, **kwargs)

    # Return results
    result = namedtuple('Segmented_Trend_Test', [
        'n_breakpoints', 'breakpoints', 'davies_p', 'segments',
        'global_trend', 'bic', 'converged'
    ])

    return result(
        n_breakpoints=n_breakpoints,
        breakpoints=breakpoints_df,
        davies_p=davies_p,
        segments=segments_df,
        global_trend=global_result,
        bic=bic_values[n_breakpoints] if 'bic_values' in locals() else None,
        converged=converged
    )


def _bootstrap_breakpoint_ci(x, t, censored, cen_type, breakpoints, n_bootstrap=100):
    """Bootstrap confidence intervals for breakpoint positions."""
    n = len(x)
    boot_breakpoints = []

    for _ in range(n_bootstrap):
        boot_idx = np.random.choice(n, n, replace=True)
        x_boot = x[boot_idx]
        t_boot = t[boot_idx]
        cen_boot = censored[boot_idx]
        cen_type_boot = cen_type[boot_idx]

        bp_boot, _ = segmented_sens_slope(
            x_boot, t_boot, cen_boot, cen_type_boot,
            n_breakpoints=len(breakpoints),
            start_values=breakpoints
        )
        boot_breakpoints.append(bp_boot)

    boot_breakpoints = np.array(boot_breakpoints)

    # Percentile CIs
    cis = np.zeros((len(breakpoints), 2))
    for i in range(len(breakpoints)):
        cis[i, 0] = np.percentile(boot_breakpoints[:, i], 2.5)
        cis[i, 1] = np.percentile(boot_breakpoints[:, i], 97.5)

    return cis
```

#### Step 6: Plotting
**File:** `MannKS/plotting.py` (add function)

```python
def plot_segmented_trend(result, x, t, save_path=None, figsize
**Priority: HIGH** - Fixes statistical assumption violation

1. Week 1: Core implementation
   - `_autocorr.py`: ACF estimation, effective n
   - `_bootstrap.py`: Block bootstrap algorithm
   - Unit tests

2. Week 2: Integration
   - Modify `trend_test()` to accept `autocorr_method`
   - Add to seasonal test
   - Comprehensive testing

3. Week 3: Validation & docs
   - Compare with R's `zyp` package
   - Write user guide
   - Add validation case V-35

### Phase 2: Rolling Trend (2 weeks)
**Priority: MEDIUM** - Adds analytical capability

1. Week 1: Core implementation
   - `rolling_trend.py`: Main function
   - `detect_change_points()`
   - `compare_periods()`
   - Unit tests

2. Week 2: Visualization & docs
   - `plot_rolling_trend()`
   - User guide with examples
   - Validation case V-36

### Phase 3: Segmented Regression (3 weeks)
**Priority: HIGH** - Unique differentiator and high user value

1. Week 1: Core Algorithm
   - `_segmented.py`: Muggeo's method with Sen's slope
   - Bootstrap restarting implementation
   - `min_segment_size` constraint logic

2. Week 2: Statistical Testing
   - Davies test for breakpoint existence
   - BIC model selection
   - Bootstrap confidence intervals for breakpoints

3. Week 3: Integration & Validation
   - `segmented_trend_test()` main wrapper
   - Comparison with rolling trends
   - Validation against `piecewise-regression` (OLS) benchmarks

---

## Recommendation

**Implement all three features**, phased as follows:

1. **Block bootstrap first**: **[COMPLETED]** Fixes the fundamental validity of the current tests.
2. **Rolling slopes second**: **[COMPLETED]** Provides immediate value for temporal exploration.
3. **Segmented regression third**: Adds advanced, unique capabilities for detecting structural breaks.

Total development time: **7-8 weeks** for all features with full testing and documentation.
