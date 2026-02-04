# v0.6.0 Audit Findings

## Issues Found

### 1. Seasonal Trend Test Crash with Aggregation + Surrogate Kwargs
**Severity:** Critical
**Description:** When `seasonal_trend_test` is used with `agg_method` (e.g., 'median') AND `surrogate_method` is used with array-like arguments (e.g., `dy` for Lomb-Scargle errors) matching the original data length, the function crashes.
**Cause:** The code attempts to pass the full-length `dy` array to the surrogate generator for a season subset (which is aggregated and much smaller). `astropy` raises `ValueError: shape mismatch`.
**Reproduction:**
```python
seasonal_trend_test(..., agg_method='median', surrogate_kwargs={'dy': full_length_errors})
```

### 2. Trend Test Silent Data Misalignment
**Severity:** High
**Description:** When `trend_test` is used with `agg_method` AND `surrogate_kwargs` (original length), the code incorrectly slices the kwargs using the aggregated dataframe's index (which is reset to `0..M-1`).
**Result:** The first `M` values of the surrogate kwargs (e.g., errors) are applied to the `M` aggregated points, which is statistically incorrect.
**Cause:** Fallback slicing logic uses `iloc` on `kept_indices` derived from `data_filtered.index`, which loses its relation to original indices after aggregation.

## Verified Behaviors
- **Surrogate Tests**: Standard surrogate tests (IAAFT, Lomb-Scargle) work correctly for standard inputs.
- **Bootstrap**: Block bootstrap works correctly for constant data (S=0) and handles sorting internally.
- **Sanitization**: `surrogate_kwargs` are properly sanitized to prevent overriding core methods.
- **Censoring**: Censored data is correctly imputed and flags propagated in surrogates.

## Recommendations
- **Fix `seasonal_trend_test.py`**: Explicitly detect length mismatch when aggregation causes loss of `original_index`. Raise `ValueError` informing the user to provide aggregated surrogate args.
- **Fix `trend_test.py`**: Similar fix to prevent incorrect slicing. Raise `ValueError` if `original_index` is missing and lengths do not match.
