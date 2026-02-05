
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch
from MannKS._surrogate import surrogate_test, _iaaft_surrogates
from MannKS.power import power_test
from scipy.stats import rankdata

def test_censoring_propagation_with_ties():
    """
    Verify that censoring status is correctly propagated to surrogates even when ties exist.
    """
    # Create data with ties: two 10s, one censored, one not.
    # value: [10, 10, 20]
    # censored: [True, False, False]
    x = np.array([10, 10, 20])
    t = np.arange(3)
    censored = np.array([True, False, False])

    n_surr = 100
    surrogates = _iaaft_surrogates(x, n_surrogates=n_surr, random_state=42)

    # Replicate the mapping logic from surrogate_test
    sort_idx = np.argsort(x, kind='stable')
    sorted_censored = censored[sort_idx]

    n = len(x)

    for i in range(n_surr):
        row = surrogates[i]
        ranks = rankdata(row, method='ordinal') - 1
        ranks = np.clip(ranks, 0, n - 1).astype(int)

        s_cen = sorted_censored[ranks]

        # Verify counts
        # We expect exactly one True (corresponding to the censored 10)
        # and two Falses (one for the uncensored 10, one for the 20)
        assert np.sum(s_cen) == 1, f"Surrogate {i} has wrong number of censored values"

        # Verify that the censored value corresponds to a '10' (min value)
        # The 20 should NEVER be censored.
        # Find index where s_cen is True
        idx_cen = np.where(s_cen)[0]
        val_cen = row[idx_cen]
        assert np.allclose(val_cen, 10), f"Surrogate {i} censored value is {val_cen}, expected 10"

def test_power_test_slope_scaling_verification():
    """
    Verify that slope scaling is applied correctly.
    If we provide slope=1 with slope_scaling='year', it should inject slope = 1/seconds_in_year per second.
    """
    x = np.random.randn(100)
    t = pd.date_range("2020-01-01", periods=100, freq="D").astype(int) / 10**9 # seconds

    # Define a slope of 365.25 units/year.
    slopes = [365.25]

    with patch('MannKS.power._iaaft_surrogates', return_value=np.zeros((1, 100))) as mock_noise:
        with patch('MannKS.power.surrogate_test') as mock_test:
            from MannKS._surrogate import SurrogateResult
            mock_test.return_value = SurrogateResult(
                method='test', original_score=0, surrogate_scores=np.zeros(10),
                p_value=0.5, z_score=0, n_surrogates=10, trend_significant=False, notes=[]
            )

            res = power_test(
                x, t, slopes=slopes, slope_scaling='year', surrogate_method='iaaft',
                n_simulations=1, n_surrogates=10, random_state=42
            )

            # Now x_injected should be exactly slope * t_centered
            x_injected = mock_test.call_args[0][0]

            # Calculate slope
            calc_slope = (x_injected[-1] - x_injected[0]) / (t[-1] - t[0])

            sec_per_year = 365.25 * 24 * 3600
            expected_slope = 365.25 / sec_per_year

            assert np.isclose(calc_slope, expected_slope, rtol=1e-5), \
                f"Slope injection failed. Got {calc_slope}, expected {expected_slope}"

def test_power_conservatism_demonstration():
    """
    Demonstrate that power_test without detrending is conservative when input data has a strong trend,
    because surrogates preserve that trend as 'noise'.
    """
    np.random.seed(42)
    n = 100
    t = np.arange(n)

    # Base noise (White noise)
    noise = np.random.normal(0, 1, n)

    # Strong trend
    slope_strong = 0.1
    trend_strong = slope_strong * t
    x_trending = trend_strong + noise

    # Pure noise (residuals)
    x_noise = noise

    slopes_to_test = [0.05]

    # Test 1: Power on trending data (Conservative)
    res_trending = power_test(
        x_trending, t, slopes=slopes_to_test,
        n_simulations=50, n_surrogates=50, random_state=42,
        surrogate_method='iaaft',
        detrend=False
    )

    # Test 2: Power on noise data (Ideal)
    res_noise = power_test(
        x_noise, t, slopes=slopes_to_test,
        n_simulations=50, n_surrogates=50, random_state=42,
        surrogate_method='iaaft'
    )

    # Expectation: Power on trending data is significantly lower
    assert res_trending.power[0] <= res_noise.power[0]

    # Quantify the gap (it was 0.12 vs 1.0)
    assert res_trending.power[0] < 0.5
    assert res_noise.power[0] > 0.8

def test_power_detrend_option():
    """
    Verify that the `detrend=True` option in power_test restores power when input has a strong trend.
    """
    np.random.seed(42)
    n = 100
    t = np.arange(n)

    noise = np.random.normal(0, 1, n)
    trend_strong = 0.1 * t
    x_trending = trend_strong + noise

    slopes_to_test = [0.05]

    # Power WITH detrending
    res_detrend = power_test(
        x_trending, t, slopes=slopes_to_test,
        n_simulations=50, n_surrogates=50, random_state=42,
        surrogate_method='iaaft',
        detrend=True
    )

    # Expectation: Power with detrending should be high (restored)
    assert res_detrend.power[0] > 0.8
