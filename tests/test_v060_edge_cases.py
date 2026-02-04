import pytest
import numpy as np
import pandas as pd
from MannKS import trend_test, seasonal_trend_test
from MannKS._surrogate import surrogate_test

def test_unsorted_aggregation_surrogate_alignment_correctness():
    """
    Test that 1-to-1 aggregation (preserving original_index) correctly aligns
    surrogate arguments even if input was unsorted.
    """
    # 1. Setup unsorted data
    t = np.array([3, 1, 5, 2, 4], dtype=float)
    x = np.array([30, 10, 50, 20, 40], dtype=float)
    dy = x * 10

    t_dt = pd.to_datetime(t, unit='D', origin='2020-01-01')

    # 2. Run trend_test with 1-to-1 aggregation (agg_period='day')
    # This should SUCCEED because _aggregate_by_group preserves original_index for singletons.
    try:
        trend_test(
            x, t_dt,
            agg_method='median',
            agg_period='day',
            surrogate_method='lomb_scargle',
            n_surrogates=10,
            surrogate_kwargs={'dy': dy}
        )
    except ValueError:
        pytest.fail("Should not raise ValueError for 1-to-1 aggregation where index is preserved")

def test_aggregation_surrogate_mismatch_error():
    """
    Test that aggregation which reduces size (losing original_index) raises ValueError
    if surrogate args (matching original length) are passed.
    """
    # Create 2 days of data, 2 points each
    t = np.array([1, 1, 2, 2], dtype=float)
    x = np.array([10, 11, 20, 21], dtype=float)
    dy = np.ones(4)

    t_dt = pd.to_datetime(t, unit='D', origin='2020-01-01')

    # Aggregate by day -> 2 points. Input -> 4 points.

    try:
        trend_test(
            x, t_dt,
            agg_method='median',
            agg_period='day',
            surrogate_method='lomb_scargle',
            n_surrogates=10,
            surrogate_kwargs={'dy': dy} # Length 4
        )
        pytest.fail("Should have raised ValueError due to aggregation size change / index loss")
    except ValueError as e:
        # We expect our new error message about aggregation
        assert "cannot be automatically mapped when aggregation" in str(e)

def test_seasonal_aggregation_surrogate_crash():
    """
    Test that seasonal_trend_test raises a clear ValueError instead of crashing
    when aggregation + surrogates are used.
    """
    # Create 2 years of daily data (730 points)
    n = 730
    t = pd.date_range(start='2020-01-01', periods=n, freq='D')
    x = np.random.randn(n)
    dy = np.ones(n) * 0.1

    # Use aggregation (e.g., median per month)
    # Use surrogate_method='lomb_scargle' with dy (length 730)

    # If the bug exists, this might crash inside Astropy or surrogate generator
    # because it passes length-730 dy to length-30 seasonal subset.

    try:
        seasonal_trend_test(
            x, t,
            period=12,
            season_type='month',
            agg_method='median', # Aggregates days to 1 value per day? No, usually agg_method is for tied timestamps OR period agg?
            # seasonal_trend_test doc says:
            # "agg_method... 'median': Aggregates to the median value."
            # "agg_period: The time period for aggregation"
            # If we just say agg_method='median' without agg_period, it aggregates tied timestamps.
            # But here timestamps are unique (daily).
            # Wait, if timestamps are unique, 'median' does nothing?
            # Unless we force aggregation via agg_period?

            # Let's use agg_period='month' to force aggregation.
            agg_period='month',

            surrogate_method='lomb_scargle',
            n_surrogates=10,
            surrogate_kwargs={'dy': dy}
        )
        # If it passes without error, it might be silently misaligning (bad) or handling it (good?)
        # But we expect it to FAIL because dy is length 730 and we aggregate to ~24 months.
        pytest.fail("Should have raised ValueError for seasonal aggregation mismatch")

    except ValueError as e:
        assert "cannot be automatically mapped" in str(e)
    except Exception as e:
        # Catch other crashes (e.g. Astropy shape mismatch)
        pytest.fail(f"Crashed with unexpected error: {e}")

def test_constant_surrogates():
    """Test surrogate generation with constant data (std=0)."""
    x = np.ones(20)
    t = np.arange(20)

    # Should not crash
    res = surrogate_test(x, t, method='iaaft', n_surrogates=10)
    assert res.original_score == 0

    # Lomb-Scargle might have issues with constant data (power=0)
    try:
        from astropy.timeseries import LombScargle
        res_ls = surrogate_test(x, t, method='lomb_scargle', n_surrogates=10)
        assert res_ls.original_score == 0
    except ImportError:
        pass

def test_all_censored_surrogates():
    """Test surrogate generation with all-censored data."""
    x = np.ones(20)
    t = np.arange(20)
    censored = np.ones(20, dtype=bool)
    cen_type = np.full(20, 'lt')

    # Should not crash
    res = surrogate_test(x, t, censored=censored, cen_type=cen_type, method='iaaft', n_surrogates=10)
    # S should be 0 for all tied (censored) values
    assert res.original_score == 0

def test_block_bootstrap_tiny_n():
    """Test block bootstrap with N=2."""
    from MannKS._bootstrap import block_bootstrap_mann_kendall

    x = np.array([1, 2])
    t = np.array([1, 2])
    censored = np.zeros(2, dtype=bool)
    cen_type = np.full(2, 'not')

    p, s, dist = block_bootstrap_mann_kendall(x, t, censored, cen_type, n_bootstrap=10)

    assert len(dist) == 10
    # With N=2, block size must be 1 or 2.
    # If 2, it's original. If 1, it's shuffled?
    # optimal_block_size forces min 3? No, min(2*corr, sqrt(n)). sqrt(2)=1.
    # But optimal_block_size returns max(block_size, 3). So it returns 3.
    # If block_size (3) > n (2), `_moving_block_bootstrap_indices` returns arange(n).
    # So every bootstrap sample is identical to original.
    # So distribution should be constant S=1.

    assert s == 1.0
    # Bootstrapped samples are detrended (null hypothesis), so S should be 0
    assert np.all(dist == 0.0)
    # S_obs = 1.0, S_boot = 0.0.
    # p = mean(|S_boot| >= |S_obs|) = mean(0 >= 1) = 0.0
    assert p == 0.0

def test_seasonal_missing_seasons():
    """Test seasonal surrogate with a season completely missing."""
    # Create data for months 1, 2, but skip 3
    t = pd.to_datetime(['2020-01-15', '2020-02-15', '2021-01-15', '2021-02-15'])
    x = np.array([1, 2, 3, 4])

    # Run seasonal trend test
    # period=12 implicit
    res = seasonal_trend_test(x, t, surrogate_method='iaaft', n_surrogates=10)

    assert res.surrogate_result is not None
    assert len(res.surrogate_result.surrogate_scores) == 10
