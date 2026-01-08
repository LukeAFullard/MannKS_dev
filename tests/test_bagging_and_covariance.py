
import pytest
import numpy as np
from MannKS.segmented_trend_test import segmented_trend_test, find_best_segmentation

def test_bagging_parameter():
    """
    Test that use_bagging=True runs and produces valid results.
    """
    np.random.seed(42)
    n = 50
    t = np.arange(n)

    # Kink at 25 (Continuous)
    # Slope 1 then Slope -1
    y = np.zeros(n)
    y[:25] = t[:25]
    y[25:] = y[24] - 1 * (t[25:] - t[24])

    y += np.random.normal(0, 0.5, n)

    # Run with bagging (Continuous default)
    res_bag = segmented_trend_test(y, t, n_breakpoints=1, use_bagging=True, n_bootstrap=20)

    # Check result structure
    assert res_bag.converged
    assert len(res_bag.breakpoints) == 1
    # Expect near 25
    assert 20 < res_bag.breakpoints[0] < 30

    assert res_bag.bootstrap_samples is not None

def test_covariance_aware_merging():
    """
    Test that covariance is calculated and affects merging.
    """
    np.random.seed(42)
    n = 60
    t = np.arange(n)

    y = t + np.random.normal(0, 5, n) # High noise, single trend

    from MannKS.segmented_trend_test import _estimate_slope_covariance, _prepare_data

    res = segmented_trend_test(y, t, n_breakpoints=1)
    bp = res.breakpoints

    df, _ = _prepare_data(y, t)
    covs = _estimate_slope_covariance(
        df['value'].to_numpy(), df['t'].to_numpy(),
        df['censored'].to_numpy(), df['cen_type'].to_numpy(),
        bp, n_bootstrap=30
    )

    assert isinstance(covs, dict)
    assert 0 in covs
    print(f"Estimated Covariance: {covs[0]}")

    res_best, _ = find_best_segmentation(y, t, max_breakpoints=1, merge_similar_segments=True, n_bootstrap=20)
    assert res_best.n_breakpoints == 0
