
import sys
import os
import time
import numpy as np
import pandas as pd
import warnings
from typing import Tuple

# Ensure we can import MannKS
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from MannKS import (
    trend_test,
    seasonal_trend_test,
    check_seasonality,
    rolling_trend_test,
    segmented_trend_test
)

def generate_large_dataset(n=190000) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    """Generate 190k points (approx 21 years of hourly data)."""
    print(f"Generating {n} points...")
    t = pd.date_range(start='2000-01-01', periods=n, freq='h')

    # Linear Trend: 0.0001 per step
    trend = 0.0001 * np.arange(n)

    # Seasonality: Annual (approx 24*365.25 hours)
    # Amplitude 10
    seasonality = 10 * np.sin(2 * np.pi * np.arange(n) / (24 * 365.25))

    # Daily seasonality just for fun (Amplitude 2)
    daily = 2 * np.sin(2 * np.pi * np.arange(n) / 24)

    # Noise
    noise = np.random.normal(0, 5, n)

    y = trend + seasonality + daily + noise

    df = pd.DataFrame({'value': y, 't': t})
    return df, y, t

def run_seasonality_test(df):
    print("\n--- 1. Seasonality Test (No Aggregation) ---")
    start = time.time()
    # Check for monthly seasonality on full hourly data (190k points)
    # This groups 190k points into 12 buckets (Jan, Feb...) and runs Kruskal-Wallis
    res = check_seasonality(
        df['value'].values,
        df['t'].values,
        season_type='month',
        period=12,
        agg_method='none' # Explicitly no aggregation
    )

    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Is Seasonal (Monthly): {res.is_seasonal}")
    print(f"p-value: {res.p_value}")
    return res

def run_trend_test(df):
    print("\n--- 2. Trend Test (Large Data Auto) ---")
    start = time.time()
    # Should automatically trigger Large Dataset Mode
    res = trend_test(
        df['value'].values,
        df['t'].values,
        large_dataset_mode='auto' # Explicitly stating auto, though it is default
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Trend: {res.trend}")
    print(f"Slope: {res.slope:.6f}")
    print(f"Computation Mode: {res.computation_mode}")
    print(f"Warnings: {res.warnings}")
    return res

def run_trend_test_forced_fast(df):
    print("\n--- 2b. Trend Test (Forced FAST Mode) ---")
    print("Testing explicit O(N log N) + Stochastic Slope on full 190k dataset...")
    start = time.time()
    res = trend_test(
        df['value'].values,
        df['t'].values,
        large_dataset_mode='fast' # Force Fast mode (Tier 2) despite N > 50k
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Trend: {res.trend}")
    print(f"Slope: {res.slope:.6f}")
    print(f"Computation Mode: {res.computation_mode}")
    print(f"Pairs Used (Stochastic): {res.pairs_used}")
    return res

def run_seasonal_trend_test(df):
    print("\n--- 3. Seasonal Trend Test ---")
    start = time.time()
    # Seasonality: Month.
    # Note: For 190k hourly points, identifying 'month' is easy.
    # It should use stratified sampling.
    res = seasonal_trend_test(
        df['value'].values,
        df['t'].values,
        season_type='month',
        period=12,
        large_dataset_mode='auto'
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Trend: {res.trend}")
    print(f"Slope: {res.slope:.6f}")
    print(f"Computation Mode: {res.computation_mode}")
    print(f"Warnings: {res.warnings}")
    return res

def run_seasonal_trend_test_forced_fast(df):
    print("\n--- 3b. Seasonal Trend Test (Forced FAST Mode) ---")
    print("Testing stratified sampling on full 190k dataset...")
    start = time.time()
    res = seasonal_trend_test(
        df['value'].values,
        df['t'].values,
        season_type='month',
        period=12,
        large_dataset_mode='fast'
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Trend: {res.trend}")
    print(f"Slope: {res.slope:.6f}")
    print(f"Computation Mode: {res.computation_mode}")
    return res

def run_rolling_trend_test(df):
    print("\n--- 4. Rolling Trend Test ---")
    # Window: 2 years (~17520 hours). Step: 6 months (~4380 hours).
    window = '17520h'
    step = '4380h'

    print(f"Window: {window}, Step: {step}")

    start = time.time()
    res_df = rolling_trend_test(
        df['value'].values,
        df['t'].values,
        window=window,
        step=step,
        large_dataset_mode='auto' # Pass down to internal tests
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Windows calculated: {len(res_df)}")
    if not res_df.empty:
        print(f"First Window Slope: {res_df.iloc[0]['slope']:.6f}")
        print(f"Last Window Slope: {res_df.iloc[-1]['slope']:.6f}")
    return res_df

def run_segmented_trend_test(df):
    print("\n--- 5. Segmented Trend Test ---")
    print("Running on full dataset (190k points)...")

    start = time.time()
    res = segmented_trend_test(
        df['value'].values,
        df['t'].values,
        max_breakpoints=3,
        n_bootstrap=10,
        large_dataset_mode='auto'
    )
    elapsed = time.time() - start
    print(f"Time: {elapsed:.2f}s")
    print(f"Breakpoints Found: {res.n_breakpoints}")
    if res.segments is not None and not res.segments.empty:
        print(f"Segments: \n{res.segments[['slope', 'intercept', 'n']]}")
    else:
        print("No segments found.")
    print(f"Computation Mode (Slope Phase): {res.computation_mode}")
    return res

def main():
    print("Initializing Large Dataset Verification (N=190,000)...")

    # Suppress internal warnings for cleaner output (we check captured warnings in results)
    # But keep UserWarnings visible
    # warnings.simplefilter("ignore")

    df, y, t = generate_large_dataset(190000)

    try:
        run_seasonality_test(df)
        run_trend_test(df)
        run_trend_test_forced_fast(df)
        run_seasonal_trend_test(df)
        run_seasonal_trend_test_forced_fast(df)
        run_rolling_trend_test(df)
        run_segmented_trend_test(df)
        print("\nAll tests completed successfully.")
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
