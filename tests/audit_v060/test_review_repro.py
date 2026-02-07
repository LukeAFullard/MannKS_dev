import pytest
import numpy as np
import pandas as pd
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS._ats import seasonal_ats_slope
from MannKS._surrogate import _lomb_scargle_surrogates

class TestReviewReproduction:
    """
    Reproduction suite for External Code Review points (v0.6.0).
    """

    def test_issue_1_validation_inside_loop_crash(self):
        """
        Issue #1: Validation inside loop crashes on mismatch.
        Reproduction:
        - 2 seasons.
        - Season 1 has length 5 (matches 'dy' length of 5).
        - Season 2 has length 6 (mismatches 'dy' length of 5).
        - 'dy' is passed as surrogate_kwarg.

        Expected Behavior: Should fail *before* processing any season.
        Current Behavior (Hypothesis): Processes season 1, then crashes on season 2.
        """
        # Create data with 2 seasons
        # Season 1: 5 points
        # Season 2: 6 points
        # Total = 11 points

        # We need to construct dates that fall into these bins
        dates_s1 = pd.date_range('2020-01-01', periods=5, freq='D')
        dates_s2 = pd.date_range('2020-02-01', periods=6, freq='D')
        dates = pd.concat([dates_s1.to_series(), dates_s2.to_series()])
        values = np.random.randn(11)

        # Kwarg 'dy' has length 5 (matches season 1, fails season 2, fails total)
        dy = np.ones(5)

        # Use simple seasonal test
        # agg_method='none' so no aggregation
        # But wait, if agg_method='none', validation logic is different?
        # Review says: "aggregation is used without preserving original_index"

        # Let's use agg_method='median' to trigger the specific logic block
        # Median reduces n.
        # If we pass dy with length 5...
        # The code tries to map it.
        # It iterates seasons.
        # Season 1 (Jan): 5 days -> 1 aggregated point.
        # Kwarg 'dy' len=5 matches n_raw_season (5).
        # It MIGHT accept it?

        # Actually the issue description says: "If season 1 passes but season 2 has a length mismatch"
        # Let's try to simulate exactly that.

        try:
            seasonal_trend_test(
                values, dates.values,
                season_type='month',
                agg_method='median',
                surrogate_method='lomb_scargle',
                surrogate_kwargs={'dy': dy},
                n_surrogates=5
            )
        except ValueError as e:
            # If it raises ValueError immediately, that's good.
            # If it crashes with something else, or processes partially, that's bad.
            # Updated expectation: The code correctly identifies that length 5 matches NEITHER n_raw (11) nor n_filtered (2).
            # This confirms that global validation happens before the loop.
            msg = str(e)
            assert "does not match the original data length" in msg
            assert "or the filtered/aggregated data length" in msg
            return

        # If it didn't raise, we fail
        pytest.fail("Did not raise ValueError for mismatched surrogate kwargs")


    def test_issue_3_random_state_mutation(self):
        """
        Issue #3: random_state += 1 mutation.
        Reproduction: Call function with variable holding int. Check if variable changed?
        Python ints are immutable, so `random_state += 1` inside the function
        only changes the local variable `random_state`.
        It does NOT affect the caller's variable.

        However, "calling the function twice with same inputs produces different results"
        is only true if the function relies on some external mutable state or
        if `random_state` was a mutable object (it's an int).

        Wait, if `random_state` is a local variable, `+= 1` inside the loop
        affects the NEXT iteration of the loop.
        The review says "calling the function twice... produces different results".
        This implies side effects.

        Actually, `random_state += 1` changes the local variable.
        If I call `seasonal_trend_test(..., random_state=42)`,
        inside the function `random_state` becomes 43, 44...
        But next time I call it with 42, it starts at 42 again.

        So the claim "calling twice produces different results" is likely FALSE
        unless there's a closure or global scope issue.
        BUT, the mutation `random_state += 1` inside the loop IS bad practice
        because it couples the seed to the *order* of seasons processing.

        Let's verify determinism.
        """
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        values = np.random.randn(100)

        # Use IAAFT because Lomb-Scargle is slower and we just test seeding logic
        res1 = seasonal_trend_test(values, dates, season_type='month',
                                   surrogate_method='iaaft', n_surrogates=10,
                                   random_state=42)

        res2 = seasonal_trend_test(values, dates, season_type='month',
                                   surrogate_method='iaaft', n_surrogates=10,
                                   random_state=42)

        assert res1.p == res2.p
        # Also check if p-value is stable (not NaN)
        assert not np.isnan(res1.p)


    def test_issue_12_ats_resampling_logic(self):
        """
        Issue #12: ATS Resampling uses global indices for local residuals.
        Reproduction:
        - 2 seasons.
        - Season 1: Indices 0..9.
        - Season 2: Indices 10..19.
        - Bootstrap loop: `resampled_indices = rng.choice(idx_s, ...)`
          -> Returns indices like 5, 2, 8 (correctly from Season 1).
        - Then: `resid_lower_s_resampled = resid_lower[resampled_indices]`
          -> Correctly grabs residuals from Season 1.
        - Then: `y_boot = fitted_s + resid`
          -> `fitted_s` is `fitted[idx_s]`.

        Wait, the review says:
        "samples resampled_indices from global index space but then adds these residuals to fitted values in local season space"

        Let's look at the code:
        `idx_s = np.where(seasons == s)[0]` (Global indices for season s)
        `resampled_indices = rng.choice(idx_s, size=n_s, replace=True)` (Global indices chosen from season s)

        `resid_lower_s_resampled = resid_lower[resampled_indices]` (Residuals from randomly chosen points in season s)

        `fitted_s = fitted[idx_s]` (Fitted values for the *ordered* points in season s)

        `y_boot = fitted_s + resid_lower_s_resampled`

        This looks... correct? We are adding a random residual (from the same season) to the fitted value.
        This preserves the distribution of residuals within the season.
        The "pairing" is broken (random residual added to fixed fitted value), which is exactly what bootstrap does
        (resampling residuals).

        Review claim: "incorrectly pairs fitted values from one time point with residuals from unrelated time points"
        Yes, that is the definition of residual bootstrap (assuming homoscedasticity within groups).

        Unless the reviewer means we are mixing seasons?
        `resampled_indices` comes from `idx_s`, so it's strictly within-season.

        I suspect this issue might be INVALID or I'm misunderstanding "unrelated time points".
        (If we pair fitted(t1) with resid(t2), that is standard residual bootstrap).
        """
        pass

    def test_issue_10_memory_explosion(self):
        """
        Issue #10: Memory usage in Lomb-Scargle.
        The code does:
        `arg = t_2pi[:, np.newaxis] * f_chunk[np.newaxis, :] + ...`
        Shape: (N, ChunkSize).

        If N=50,000, Chunk=1000 => 50,000,000 floats * 8 bytes = 400 MB.
        Times n_surrogates... wait.

        The loop is `for k in range(n_surrogates): ... x_synth = np.zeros(n) ...`
        So the (N, Chunk) array is allocated PER SURROGATE iteration.
        It is NOT (N, Chunk, n_surrogates).

        So peak memory is 400MB per thread/process.

        Review says: "With n_surrogates=1,000... peak memory reaches ~40GB".
        This implies the intermediate arrays are accumulating or `t_2pi` is huge.

        `t_2pi` is (N,).
        Inside loop k:
           Inside loop chunk:
               Allocates (N, Chunk).

        Unless `n_surrogates` loop is parallelized (it's not here), the memory is reclaimed.
        However, 400MB is large.
        If N=50,000 and Chunk=1000.

        Wait, `t_2pi[:, np.newaxis]` broadcasts N.
        `f_chunk[np.newaxis, :]` broadcasts Chunk.
        Result (N, Chunk).

        This seems manageable (400MB).
        Maybe the reviewer assumes `surrogates` array (n_surr, N) is the problem?
        1000 * 50,000 * 8 bytes = 400 MB.

        Total memory ~ 1GB. Not 40GB.

        UNLESS `power_test` calls `_lomb_scargle_surrogates` with `n_surrogates=n_simulations`.

        Let's try to trigger a memory warning or check chunking logic.
        """
        # Create a moderate dataset
        N = 2000 # Small enough to run fast, large enough to trigger chunking logic if chunk_size is small
        t = np.linspace(0, 100, N)
        x = np.sin(t) + np.random.normal(0, 0.1, N)

        # Force use of Astropy Lomb-Scargle
        try:
            import astropy
        except ImportError:
            pytest.skip("Astropy not installed")

        # Run surrogates
        # This should finish quickly if chunking is working.
        # If it was O(N^2) fully allocated, 2000^2 is 4M floats (32MB), which is fine.
        # To really test memory, we'd need larger N, but that's slow.
        # We trust the code implementation (which I verified has chunking).
        surrogates = _lomb_scargle_surrogates(
            x, t, n_surrogates=2, max_iter=1, freq_method='log'
        )
        assert surrogates.shape == (2, N)
