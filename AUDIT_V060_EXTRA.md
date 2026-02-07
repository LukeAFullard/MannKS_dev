# v0.6.0 Audit Extra Findings

This document summarizes the additional audit findings and fixes performed for v0.6.0 features.

## Findings

1.  **Scalar Surrogate Arguments with Aggregation in `trend_test`**:
    -   **Issue**: `trend_test` raised a `ValueError` when `agg_method` was not `'none'` (e.g., `'median'`) and any `surrogate_kwargs` were provided, even if they were scalars (e.g., `dy=0.1`). This was overly restrictive, as scalars do not require mapping to the aggregated data.
    -   **Fix**: Modified `MannKS/trend_test.py` to only raise `ValueError` if an array-like argument matching the original data length (`n_raw`) is detected in `surrogate_kwargs`. This ensures safety against misalignment while allowing valid scalar parameters.
    -   **Verification**: Added `tests/audit_v060/test_v060_audit_extra.py` with `test_trend_test_median_scalar_kwargs`.

2.  **Array Surrogate Arguments with LWP Aggregation in `seasonal_trend_test`**:
    -   **Finding**: Confirmed that `seasonal_trend_test` correctly handles array-like `surrogate_kwargs` when using `agg_method='lwp'` because the LWP aggregation method preserves the `original_index` column.
    -   **Verification**: Added `test_seasonal_trend_test_lwp_kwargs`.

3.  **IAAFT Iterations**:
    -   **Finding**: Confirmed that `surrogate_test` correctly overrides the default `max_iter=1` (intended for Lomb-Scargle) to `max_iter=100` for IAAFT, unless explicitly set by the user.
    -   **Verification**: Added `test_iaaft_max_iter_override`.

4.  **Power Analysis**:
    -   **Finding**: Verified slope scaling logic and reproducibility in `power_test` via existing and new audit tests.

## Conclusion

The v0.6.0 features (`power_test`, `surrogate_test`, updated `trend_test`/`seasonal_trend_test`) have been audited. A blocking issue for scalar surrogate arguments in `trend_test` was fixed. All other behaviors were verified to be correct and robust. The package is considered production-ready for these features.
