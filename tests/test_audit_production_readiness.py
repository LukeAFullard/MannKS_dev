
import numpy as np
import pandas as pd
import pytest
import warnings
from MannKS import trend_test

def test_audit_boundary_exactness():
    """
    Verify that N=5000 (Full) and N=5001 (Fast MK Score) produce mathematically
    consistent MK Scores (S) and Variances.

    The 'Fast' MK score for uncensored data uses an O(N log N) algorithm which
    should be EXACTLY equal to the O(N^2) algorithm, not an approximation.
    """
    np.random.seed(42)

    # Case 1: N = 5000 (Uses Full Mode by default)
    n1 = 5000
    x1 = np.random.normal(0, 1, n1)
    t1 = np.arange(n1)

    res1 = trend_test(x1, t1)

    # Case 2: N = 5000 (Forced Fast Mode)
    # This forces the O(N log N) MK calculation even for N=5000
    # The S and VarS should be IDENTICAL to Full Mode.
    res2 = trend_test(x1, t1, large_dataset_mode='fast')

    # Use approx for floating point safety, though they should be mathematically identical
    assert res1.s == pytest.approx(res2.s), "MK Score mismatch between Full and Forced Fast mode"
    assert res1.var_s == pytest.approx(res2.var_s), "Variance mismatch between Full and Forced Fast mode"

def test_audit_determinism():
    """
    Verify that setting random_state ensures bit-exact reproducibility
    for stochastic components (Fast Sen's Slope).
    """
    n = 6000 # Triggers fast mode
    x = np.random.normal(0, 1, n)
    t = np.arange(n)

    seed = 12345

    res1 = trend_test(x, t, random_state=seed)
    res2 = trend_test(x, t, random_state=seed)

    assert res1.slope == res2.slope, "Slopes are not identical with same seed!"
    assert res1.lower_ci == res2.lower_ci, "CIs are not identical with same seed!"

    # Verify different seed gives different result
    res3 = trend_test(x, t, random_state=seed+1)
    assert res1.slope != res3.slope, "Slopes should differ with different seeds (extremely unlikely to be identical)"

def test_audit_heavy_ties():
    """
    Verify behavior with heavy ties.
    The O(N log N) implementation warns if ties > 50%.
    """
    n = 6000
    # Create 80% ties
    x = np.zeros(n)
    indices = np.random.choice(n, int(n*0.2), replace=False)
    x[indices] = np.random.normal(0, 1, int(n*0.2))
    t = np.arange(n)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        res = trend_test(x, t)

        # Check for the specific warning
        tie_warnings = [str(warn.message) for warn in w if "Heavy ties detected" in str(warn.message)]
        if not tie_warnings:
             # Check if it's in the result warnings
             assert any("Heavy ties detected" in str(rw) for rw in res.warnings), "Did not detect heavy ties warning."

def test_audit_censored_fallback():
    """
    Verify that censored data falls back to appropriate algorithms.
    For N > 5000 with censored data:
    1. MK Score: Cannot use O(N log N). Must use Chunked O(N^2) or standard.
    2. Slope: Can use Stochastic Censored Slope.
    """
    n = 6000
    x = np.random.normal(0, 1, n)
    t = np.arange(n)
    censored = np.zeros(n, dtype=bool)
    censored[::10] = True # 10% censored

    # Explicitly creating cen_type column as expected by _prepare_data if we pass a DataFrame
    cen_type = np.full(n, 'not', dtype=object)
    cen_type[censored] = 'lt' # Assuming left-censored for test

    df = pd.DataFrame({'value': x, 't': t, 'censored': censored, 'cen_type': cen_type})

    res = trend_test(df, t=df['t'], large_dataset_mode='auto', random_state=42)

    # It should still be 'fast' because 'fast' mode refers to the OVERALL strategy
    # (stochastic slope), even if MK score had to fallback.
    assert res.computation_mode == 'fast'

    assert res.pairs_used is not None
    assert res.pairs_used <= 100000 + 100 # buffer

def test_audit_seasonal_stratification_detail():
    """
    Verify that seasonal stratification produces the exact expected sample sizes.
    """
    # 2 seasons, unbalanced.
    # Season 1: 10,000 points
    # Season 2: 10,000 points
    # Max per season: 500
    # Expected total: 1000

    n_per_season = 10000
    s1 = pd.DataFrame({'value': np.random.randn(n_per_season), 'season': 1, 't': np.arange(n_per_season)})
    s2 = pd.DataFrame({'value': np.random.randn(n_per_season), 'season': 2, 't': np.arange(n_per_season, 2*n_per_season)})

    df = pd.concat([s1, s2])

    # We call the internal function directly to verify exact logic
    from MannKS._large_dataset import stratified_seasonal_sampling

    sampled = stratified_seasonal_sampling(df, season_col='season', max_per_season=500, random_state=99)

    counts = sampled['season'].value_counts()

    assert counts[1] == 500
    assert counts[2] == 500
    assert len(sampled) == 1000
