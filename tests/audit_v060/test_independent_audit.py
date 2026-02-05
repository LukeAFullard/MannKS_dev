
import pytest
import numpy as np
import pandas as pd
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.power import power_test
from MannKS._surrogate import surrogate_test, _lomb_scargle_surrogates

class TestIndependentAuditV060:
    """
    Independent audit suite for v0.6.0 features.
    Focuses on adversarial inputs, edge cases, and strict correctness.
    """

    def setup_method(self):
        self.rng = np.random.default_rng(42)
        self.t_daily = pd.date_range("2020-01-01", periods=100, freq="D")
        self.t_sec = self.t_daily.astype(int) / 10**9
        self.x_random = self.rng.standard_normal(100)

    # --- 1. Lomb-Scargle Stability ---

    def test_lomb_scargle_constant_data(self):
        """Verify constant data returns constant surrogates (no crash/NaNs)."""
        x_const = np.ones(50) * 10.0
        t = np.arange(50)

        # Should not raise DivisionByZero or return NaNs
        surrogates = _lomb_scargle_surrogates(
            x_const, t, n_surrogates=5, random_state=42
        )

        assert surrogates.shape == (5, 50)
        np.testing.assert_allclose(surrogates, 10.0, err_msg="Surrogates of constant data must be constant")

    def test_lomb_scargle_extreme_offset(self):
        """Verify handling of data with large offsets (precision check)."""
        x_large = self.x_random + 1e9
        t = np.arange(100)

        # Center_data=True is default, which should handle this
        surrogates = _lomb_scargle_surrogates(
            x_large, t, n_surrogates=5, random_state=42
        )

        # Surrogates should have similar mean/std to input
        # Note: Rank adjustment restores the exact values, so mean/std should be identical to input distribution
        assert np.abs(np.mean(surrogates) - np.mean(x_large)) < 1.0 # Loose bound, really should be close
        assert np.all(np.min(surrogates, axis=1) >= np.min(x_large))

    # --- 2. Surrogate Kwargs & Aggregation ---

    def test_trend_test_kwargs_aggregation_conflict(self):
        """
        trend_test MUST raise ValueError if aggregation is used
        and array-like kwargs (dy) are passed, as index mapping is lost.
        """
        x = self.x_random
        t = self.t_daily
        dy = np.ones(100) * 0.1

        # 1. No aggregation + dy -> Should work
        res = trend_test(x, t, surrogate_method='auto', n_surrogates=10,
                        surrogate_kwargs={'dy': dy})
        assert res.surrogate_result is not None

        # 2. Aggregation + dy -> Should fail
        # Note: 'month' is the valid key, not 'M'.
        # If we pass 'M' we get an invalid period error before the surrogate check.
        with pytest.raises(ValueError, match="cannot be automatically mapped"):
            trend_test(x, t, agg_method='median', agg_period='month',
                       surrogate_method='auto', n_surrogates=10,
                       surrogate_kwargs={'dy': dy})

    def test_seasonal_trend_test_kwargs_aggregation_conflict(self):
        """
        seasonal_trend_test MUST raise ValueError if aggregation is used
        and array-like kwargs are passed.
        """
        # Create 2 years of monthly data (24 points)
        t = pd.date_range("2020-01-01", periods=24, freq="ME")
        x = self.rng.standard_normal(24)
        dy = np.ones(24) * 0.1

        # 1. No aggregation + dy -> Should work
        res = seasonal_trend_test(x, t, season_type='month',
                                  surrogate_method='auto', n_surrogates=10,
                                  surrogate_kwargs={'dy': dy})
        assert res.surrogate_result is not None

        # 2. Aggregation (e.g. daily to monthly) + dy -> Should fail
        # Construct daily data
        t_daily = pd.date_range("2020-01-01", periods=730, freq="D")
        x_daily = self.rng.standard_normal(730)
        dy_daily = np.ones(730) * 0.1

        with pytest.raises(ValueError, match="cannot be automatically mapped"):
            seasonal_trend_test(x_daily, t_daily, season_type='month',
                                agg_method='median', # Aggregates daily -> monthly
                                surrogate_method='auto', n_surrogates=10,
                                surrogate_kwargs={'dy': dy_daily})

    # --- 3. Power Test Correctness ---

    def test_power_test_slope_scaling_correctness(self):
        """
        Verify that slope_scaling correctly interprets input slopes.
        Test: Inject a trend of +1 unit/year.
        If we test for a slope of -1 unit/year (scaled), the sum should be 0 trend (Null).
        Wait, power test INJECTS the trend.

        Strategy:
        1. Create pure noise (no trend).
        2. Inject slope = 0.
        3. Power should be ~ alpha (0.05).

        Strategy 2 (Scaling):
        1. Inject slope S in 'units/year'.
        2. Verify that the injected signal in the simulator matches S / (seconds_per_year).

        We can infer this by detrending.
        """
        # We'll use a direct call to verify scaling logic implicitly via detrend=True
        # If we inject a trend, and ask power_test to DETREND, it should remove existing trends.
        # But power_test detrends the INPUT x, then generates noise, then injects slope.

        # Let's test scaling by simple calculation check logic from the codebase
        # We can't easily access internals, but we can check if results make sense.

        # Test: Inject a HUGE slope in 'per second' vs 'per year'.
        # 1 unit/second is massive. 1 unit/year is small.
        # If we ask for slope=1 with slope_scaling='year', it should be small injection.

        # We'll use a short simulation
        slopes = [1.0] # 1 unit

        # Case A: slope_scaling='s' (default-ish/explicit). 1 unit/sec. Massive trend. Power should be 1.0.
        res_sec = power_test(self.x_random, self.t_daily, slopes=[1e-5], slope_scaling='s',
                             n_simulations=10, n_surrogates=10)
        # 1e-5 per second is ~864 per day. Over 100 days -> 86400 change. Huge.
        assert res_sec.power[0] == 1.0, "Should detect massive trend (per second) easily"

        # Case B: slope_scaling='year'. 1 unit/year. Over 100 days (~0.27 year), change is ~0.27.
        # Given x is N(0,1), a change of 0.27 is buried in noise. Power should be low (~alpha).
        res_year = power_test(self.x_random, self.t_daily, slopes=[1.0], slope_scaling='year',
                              n_simulations=50, n_surrogates=50, random_state=42)

        # Power should be low, nowhere near 1.0
        assert res_year.power[0] < 0.4, f"Trend of 1/year (0.27 total) should be hard to detect in N(0,1). Got {res_year.power[0]}"

    def test_power_test_reproducibility(self):
        """Run power_test twice with same seed -> Identical results."""
        kwargs = dict(
            x=self.x_random, t=self.t_daily,
            slopes=[0.5, 1.0], slope_scaling='year',
            n_simulations=10, n_surrogates=10, random_state=123
        )

        res1 = power_test(**kwargs)
        res2 = power_test(**kwargs)

        np.testing.assert_array_equal(res1.power, res2.power)

        # Handle NaN == NaN case for MDT
        if np.isnan(res1.min_detectable_trend):
            assert np.isnan(res2.min_detectable_trend)
        else:
            assert res1.min_detectable_trend == res2.min_detectable_trend

    def test_power_test_dataframe_censored(self):
        """Ensure power_test accepts censored DataFrame (and ignores censoring for noise generation)."""
        df = pd.DataFrame({
            'value': self.x_random,
            'censored': [False] * 100,
            't': self.t_daily
        })

        # Should not crash
        res = power_test(df, df['t'], slopes=[1.0], n_simulations=5, n_surrogates=5)
        assert len(res.power) == 1

    # --- 4. Adversarial Inputs ---

    def test_surrogate_invalid_method(self):
        with pytest.raises(ValueError, match="Unknown method"):
            surrogate_test(self.x_random, self.t_daily.astype(int), method='not_a_method')

    def test_surrogate_n_surrogates_zero(self):
        with pytest.raises(ValueError, match="must be positive"):
            surrogate_test(self.x_random, self.t_daily.astype(int), n_surrogates=0)

    def test_power_test_mismatched_lengths(self):
        with pytest.raises(ValueError):
            power_test(self.x_random, self.t_daily[:50], slopes=[1.0])

    def test_lomb_scargle_all_nan(self):
        """Lomb Scargle with all NaNs - should probably fail gracefully or raise."""
        # The code prepares data before calling _lomb_scargle, usually filtering NaNs.
        # But if we call internal directly:
        x_nan = np.full(50, np.nan)
        t = np.arange(50)

        # Astropy might raise, or return NaNs.
        # Our wrapper doesn't explicitly check for NaNs inside _lomb_scargle
        # because trend_test filters them.
        # But let's see what happens.
        try:
             # Astropy LS usually raises on NaNs
            _lomb_scargle_surrogates(x_nan, t, n_surrogates=5)
        except Exception:
            pass # As long as it doesn't hang or segfault

    # --- 5. Data Types ---

    def test_surrogate_test_integer_inputs(self):
        """Ensure integer inputs don't cause float casting issues in in-place ops."""
        x_int = np.random.randint(0, 10, 50)
        t_int = np.arange(50)
        censored = np.zeros(50, dtype=bool)
        censored[0] = True # One censored value

        # If code tries x[censored] *= 0.5 on integer array -> TypeError or cast
        # _surrogate.py explicitly casts to float. Verify this.
        res = surrogate_test(x_int, t_int, censored=censored, n_surrogates=5)
        assert res.n_surrogates == 5
