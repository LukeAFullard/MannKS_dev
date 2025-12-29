# Bug: `trend_test` ignores `agg_period` when `agg_method` is 'median'

## Observed Behavior in Example 8

In "Example 8: Aggregation for Tied and Clustered Data", we attempt to demonstrate the difference between simple median aggregation for tied timestamps (Test 2) and monthly aggregation (Test 3).

*   **Test 2:** `agg_method='median'` (Default `agg_period`)
    *   Expected: Aggregates only exact duplicate timestamps.
    *   Result: Slope: 6.38199, P-value: 0.00000
*   **Test 3:** `agg_method='median'`, `agg_period='month'`
    *   Expected: Aggregates all data points within the same month to a single value.
    *   Result: Slope: 6.38199, P-value: 0.00000 (Identical to Test 2)

The identical results strongly suggest that Test 3 did **not** perform monthly aggregation and instead defaulted to the same behavior as Test 2 (aggregating only exact timestamp matches).

## Code Analysis

The issue lies in `MannKS/trend_test.py`.

The code handles `lwp`-style aggregation (which inherently uses `agg_period`) in a dedicated block:

```python
    # Handle tied timestamps and temporal aggregation
    if agg_method in ['lwp', 'lwp_median', 'lwp_robust_median']:
        # ... logic that uses agg_period ...
```

However, for standard aggregation methods like `'median'`, it falls into the `elif` block:

```python
    elif len(data_filtered['t']) != len(np.unique(data_filtered['t'])):
        # ...
            agg_data_list = [
                _aggregate_by_group(group, agg_method, is_datetime)
                for _, group in data_filtered.groupby('t')
            ]
```

**Critical Flaw:** The standard aggregation block explicitly groups by `'t'` (the timestamp column). This means it **always** groups by exact timestamp match. It **does not** check or use the `agg_period` parameter to create a broader grouping key (e.g., 'YYYY-MM') before grouping.

As a result, `agg_period` is effectively ignored unless `agg_method` is one of the `lwp` variants.

## Steps to Reproduce

1.  Create a dataset with clustered data (e.g., multiple distinct timestamps within the same month).
2.  Run `trend_test(x, t, agg_method='median', agg_period='month')`.
3.  Run `trend_test(x, t, agg_method='median')`.
4.  Observe that the results (slope, p-value, sample size) are identical, confirming that the monthly grouping was not applied.

## Recommendation

The `trend_test` function needs to be refactored to support `agg_period` for standard aggregation methods (`median`, `mean`, etc.).

1.  If `agg_period` is provided (and not default/None), construct a `group_key` based on that period (similar to the LWP block).
2.  Use that `group_key` for the `.groupby()` operation instead of `'t'`.
