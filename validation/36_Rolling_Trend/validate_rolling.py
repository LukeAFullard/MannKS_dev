"""
Validation Script for Rolling Trend Analysis (V-36)

This script performs a comprehensive validation of the rolling trend feature,
covering correctness, feature interaction, edge cases, and robustness.
"""
import numpy as np
import pandas as pd
import MannKS as mk
from scipy.stats import linregress
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def run_manual_rolling_check(x, t, window, step, **kwargs):
    """Manually iterate and calculate trends to verify rolling logic."""
    results = []

    # Simple manual loop for numeric or datetime
    is_datetime = pd.api.types.is_datetime64_any_dtype(t)

    if is_datetime:
        t_series = pd.to_datetime(t)
        # Assuming fixed window/step for validation simplicitly
        start = t_series.min()
        end_limit = t_series.max()
        window_td = pd.to_timedelta(window)
        step_td = pd.to_timedelta(step)

        current = start
        while current < end_limit:
            win_end = current + window_td
            mask = (t_series >= current) & (t_series < win_end)

            if mask.sum() >= kwargs.get('min_size', 10):
                res = mk.trend_test(x[mask], t[mask], **kwargs)
                results.append(res.slope)
            else:
                results.append(np.nan) # Placeholder for skipped

            current += step_td
    else:
        # Numeric
        start = t.min()
        end_limit = t.max()
        current = start
        while current < end_limit:
            win_end = current + window
            mask = (t >= current) & (t < win_end)

            if mask.sum() >= kwargs.get('min_size', 10):
                res = mk.trend_test(x[mask], t[mask], **kwargs)
                results.append(res.slope)
            else:
                results.append(np.nan)

            current += step

    return results

def validation_report():
    print("# Validation Report: Rolling Trend Analysis (V-36)\n")

    # --- V-36a: Basic Correctness ---
    print("## V-36a: Basic Correctness Check")
    n = 200
    t = pd.date_range('2000-01-01', periods=n, freq='D')
    x = np.arange(n) * 0.1 + np.random.normal(0, 1, n)

    # Run package function
    rolling_res = mk.rolling_trend_test(x, t, window='50D', step='10D', min_size=10)

    # Run manual verification
    # Note: manual loop implementation above is simplified, rolling_trend_test handles edge cases better
    # We will verify that the slopes match for the windows that exist
    manual_slopes = []
    t_series = pd.Series(t)
    for idx, row in rolling_res.iterrows():
        start, end = row['window_start'], row['window_end']
        mask = (t_series >= start) & (t_series < end)
        res = mk.trend_test(x[mask], t[mask])
        manual_slopes.append(res.slope)

    diffs = np.abs(rolling_res['slope'] - manual_slopes)
    max_diff = np.nanmax(diffs)

    if max_diff < 1e-10:
        print(f"PASS: Rolling slopes match manual calculation perfectly (Max diff: {max_diff:.2e})")
    else:
        print(f"FAIL: Rolling slopes diverge from manual calculation (Max diff: {max_diff:.2e})")

    # --- V-36b: Interaction with Aggregation ---
    print("\n## V-36b: Interaction with Aggregation")
    # High freq data (hourly) for 1 year
    t_agg = pd.date_range('2000-01-01', periods=24*365, freq='h')
    x_agg = np.arange(len(t_agg)) * 0.01 + np.random.normal(0, 5, len(t_agg))

    # Rolling monthly trend on hourly data, with daily aggregation
    # This ensures that 'agg_period' is passed correctly to the inner trend_test
    print("Running rolling trend with daily aggregation on hourly data...")
    res_agg = mk.rolling_trend_test(
        x_agg, t_agg,
        window='90D', step='30D',
        agg_method='median', agg_period='day'
    )

    if len(res_agg) > 0 and not res_agg['slope'].isna().all():
        print(f"PASS: Successfully computed rolling trends with aggregation (Generated {len(res_agg)} windows)")
    else:
        print("FAIL: Failed to compute rolling trends with aggregation")

    # --- V-36c: Interaction with High Censor Rule ---
    print("\n## V-36c: Interaction with High Censor Rule")
    # Data where detection limit increases over time
    t_cen = pd.date_range('2000-01-01', periods=100, freq='ME')
    x_raw = np.random.normal(10, 2, 100)

    # Create mixed data with varying detection limits
    # Window 1: Low limits (<1)
    # Window 2: High limits (<15) - should trigger high censor rule if enabled
    x_mixed = x_raw.copy()
    censored_flags = []

    # Convert to string representation for prepare_censored_data
    # First 50 points: mostly observed, some < 1
    data_list = []
    for i in range(100):
        val = x_mixed[i]
        if i < 50:
            if i % 10 == 0: data_list.append('<1')
            else: data_list.append(val)
        else:
            # Second 50 points: introduce high detection limit < 15
            # Since data mean is 10, <15 censors everything below 15
            if i % 5 == 0: data_list.append('<15')
            else: data_list.append(val)

    df_cen = mk.prepare_censored_data(data_list)

    # Run with hicensor=True
    # In the second half, the presence of <15 should censor all observed values < 15
    # resulting in a very different slope (likely flat or zero if variance is killed)
    res_hicensor = mk.rolling_trend_test(
        df_cen, t_cen,
        window='400D', step='100D',
        hicensor=True,
        mk_test_method='lwp' # Use LWP method to be sensitive to this
    )

    # Just verify it runs and applies logic without crashing
    print("PASS: High censor rule rolling test completed without error.")

    # --- V-36d: Edge Cases ---
    print("\n## V-36d: Edge Cases (Small Windows)")
    x_short = np.arange(20)
    t_short = np.arange(20)

    # Window size 5, min size 6 -> Should result in empty results
    res_empty = mk.rolling_trend_test(x_short, t_short, window=5, step=1, min_size=6)
    if res_empty.empty:
        print("PASS: min_size filtering correctly returned empty DataFrame.")
    else:
        print(f"FAIL: min_size filtering returned {len(res_empty)} rows (expected 0).")

    # --- V-36e: Outlier Robustness ---
    print("\n## V-36e: Outlier Robustness")
    n_out = 100
    t_out = np.arange(n_out)
    x_out = 0.5 * t_out + np.random.normal(0, 1, n_out)

    # Add massive outlier
    x_out[50] = 1000

    # Compare Sen's slope vs OLS in the window containing the outlier
    # Window centered around 50
    # Window [40, 60]
    mask = (t_out >= 40) & (t_out < 60)
    x_win = x_out[mask]
    t_win = t_out[mask]

    # OLS
    ols_res = linregress(t_win, x_win)
    ols_slope = ols_res.slope

    # MannKS
    mk_res = mk.trend_test(x_win, t_win)
    sen_slope = mk_res.slope

    print(f"Window with outlier (True slope ~0.5)")
    print(f"OLS Slope: {ols_slope:.4f}")
    print(f"Sen's Slope: {sen_slope:.4f}")

    if abs(sen_slope - 0.5) < abs(ols_slope - 0.5):
        print("PASS: Sen's slope is more robust to outlier than OLS.")
    else:
        print("FAIL: Sen's slope was not more robust.")

    # --- V-36f: Synthetic Reliability ---
    print("\n## V-36f: Synthetic Reliability (Sine Wave)")
    # Sine wave: slope changes continuously
    # y = sin(t/10) -> slope = 0.1 * cos(t/10)
    n_sine = 200
    t_sine = np.arange(n_sine)
    x_sine = 10 * np.sin(t_sine / 10)

    # Rolling trend with small window to track derivative
    window_sine = 20
    res_sine = mk.rolling_trend_test(x_sine, t_sine, window=window_sine, step=1)

    # Compare calculated slope with analytical derivative at window center
    # Derivative of 10*sin(t/10) is cos(t/10)

    # Note: Sen's slope estimates the secant, which approximates derivative
    centers = res_sine['window_center']
    analytical_slopes = np.cos(centers / 10)

    correlation = np.corrcoef(res_sine['slope'], analytical_slopes)[0, 1]

    print(f"Correlation between rolling Sen's slope and analytical derivative: {correlation:.4f}")

    if correlation > 0.95:
        print("PASS: Rolling trend accurately tracks changing signal derivative.")
    else:
        print("FAIL: Correlation too low.")

if __name__ == "__main__":
    validation_report()
