
import pytest
import numpy as np
import pandas as pd
import MannKS._bootstrap as bootstrap
from MannKS._stats import _mk_score_and_var_censored
from MannKS.trend_test import trend_test

def test_optimal_block_size():
    # Test with uncorrelated data
    np.random.seed(42)
    x = np.random.randn(100)
    acf = np.zeros(10)
    # Mocking ACF estimation logic (just testing the math in optimal_block_size)
    # The function calls estimate_acf internally if 'auto' is passed to the main function,
    # but optimal_block_size takes n and acf as input.

    # Case 1: No autocorrelation
    acf[0] = 1.0
    acf[1:] = 0.05
    bs = bootstrap.optimal_block_size(100, acf)
    assert bs >= 3 # Min block size
    assert bs == 3 # 2 * corr_length (1) = 2, but min is 3

    # Case 2: Autocorrelation up to lag 3
    acf[1] = 0.5
    acf[2] = 0.2
    acf[3] = 0.05
    # corr_length should be 3 (first lag < 0.1)
    bs = bootstrap.optimal_block_size(100, acf)
    assert bs == 6 # 2 * 3 = 6

def test_moving_block_bootstrap_indices():
    n = 10
    block_size = 3
    indices = bootstrap._moving_block_bootstrap_indices(n, block_size)
    assert len(indices) == n
    assert np.all(indices >= 0)
    assert np.all(indices < n)

    # Check if indices are consecutive in blocks of 3 (mostly)
    # This is stochastic, but we can check basic properties
    diffs = np.diff(indices)
    # In a block of 3, we expect +1 differences twice, then a jump.
    # So count of (diff == 1) should be substantial.
    assert np.sum(diffs == 1) >= (n // block_size) * (block_size - 1)

def test_bootstrap_mk_censored_alignment():
    """Verify that censored flags move with values."""
    x = np.array([10.0, 30.0])
    t = np.array([0, 1])
    censored = np.array([False, True])
    cen_type = np.array(['none', '<'])

    # Monkeypatch MK to capture inputs
    captured_x = []
    captured_censored = []

    original_mk = bootstrap._mk_score_and_var_censored

    def mock_mk(x_in, t_in, censored_in, cen_type_in, **kwargs):
        captured_x.append(x_in.copy())
        captured_censored.append(censored_in.copy())
        return 0, 0, 0, 0

    bootstrap._mk_score_and_var_censored = mock_mk

    # Force block size 1, so we shuffle individual elements
    bootstrap.block_bootstrap_mann_kendall(x, t, censored, cen_type,
                                           block_size=1, n_bootstrap=10)

    bootstrap._mk_score_and_var_censored = original_mk

    # Check alignment
    for i in range(len(captured_x)): # skip first call (observed)
        x_boot = captured_x[i]
        c_boot = captured_censored[i]

        for val, is_cen in zip(x_boot, c_boot):
            if val == 10.0: # Should be False
                assert not is_cen, f"Value 10.0 should be uncensored, got {is_cen}"
            elif val == 30.0: # Should be True (was 30 in original setup)
                # Wait, detrending changes values.
                # In this test, we didn't mock detrending.
                # N=2, x=[10, 30], t=[0, 1]. Slope = 20.
                # t_centered = [-0.5, 0.5].
                # x_detrended = [10 - 20*(-0.5), 30 - 20*(0.5)] = [10+10, 30-10] = [20, 20].
                # If detrended values are identical, we can't distinguish them.
                pass

    # Rerun with distinct detrended values
    # x=[10, 30], slope forced to 0
    bootstrap._mk_score_and_var_censored = mock_mk
    original_sen = bootstrap._sens_estimator_censored
    bootstrap._sens_estimator_censored = lambda *args: [0.0]

    captured_x = []
    captured_censored = []

    bootstrap.block_bootstrap_mann_kendall(x, t, censored, cen_type,
                                           block_size=1, n_bootstrap=10)

    bootstrap._mk_score_and_var_censored = original_mk
    bootstrap._sens_estimator_censored = original_sen

    # Skip the first call (observed statistic)
    for i in range(1, len(captured_x)):
        x_boot = captured_x[i]
        c_boot = captured_censored[i]

        for val, is_cen in zip(x_boot, c_boot):
            if val == 10.0:
                assert not is_cen
            elif val == 30.0:
                assert is_cen

def test_surrogate_with_block_bootstrap_coexistence():
    """
    Verify that surrogate testing and block bootstrap can be requested simultaneously.
    """
    n = 50
    t = np.arange(n)
    x = 0.1 * t + np.random.randn(n)

    result = trend_test(
        x, t,
        autocorr_method='block_bootstrap',
        n_bootstrap=100,
        surrogate_method='iaaft',
        n_surrogates=100
    )

    # Check if both ran
    assert result.block_size_used is not None # Indicates bootstrap ran
    assert result.surrogate_result is not None # Indicates surrogate ran
    assert result.surrogate_result.method == 'iaaft'

def test_block_bootstrap_censored_data():
    """
    Verify block bootstrap runs with censored data.
    """
    n = 50
    t = np.arange(n)
    x = 0.1 * t + np.random.randn(n)

    # Add censoring
    censored = np.zeros(n, dtype=bool)
    censored[0:5] = True # First 5 points censored

    df = pd.DataFrame({
        'value': x,
        'censored': censored,
        'cen_type': ['lt'] * n
    })

    result = trend_test(
        df, t,
        autocorr_method='block_bootstrap',
        n_bootstrap=50
    )

    assert result.trend is not None
    assert result.block_size_used is not None
