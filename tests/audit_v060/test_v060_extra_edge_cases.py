
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.power import power_test
from MannKS._surrogate import surrogate_test

class TestNewEdgeCases:

    def test_lomb_scargle_invalid_params(self):
        """Test Lomb-Scargle surrogate generation with invalid parameters."""
        x = np.random.randn(50)
        t = np.arange(50)

        # Invalid normalization
        with pytest.raises(ValueError):
            surrogate_test(x, t, method='lomb_scargle', normalization='invalid_norm')

    def test_trend_test_misaligned_kwargs(self):
        """Test trend_test with misaligned surrogate kwargs."""
        x = np.random.randn(50)
        t = np.arange(50)

        # Case 1: dy has wrong length (not N, not filtered N)
        # Should be passed as is, but might cause error inside if implementation uses it strictly
        # or if validation allows it but then it crashes.
        # Actually, trend_test validation says:
        # If length matches N_raw, try to map.
        # If length matches N_filt, use it.
        # Else pass as is.

        # If we pass dy of length 40 (mismatch), it is passed to surrogate_test.
        # surrogate_test -> _lomb_scargle_surrogates -> LombScargle(..., dy=dy)
        # Astropy will likely raise ValueError if dy length mismatch.

        dy_wrong = np.ones(40)

        with pytest.raises((ValueError, Exception)):
             trend_test(x, t, surrogate_method='lomb_scargle', surrogate_kwargs={'dy': dy_wrong})

    def test_seasonal_trend_test_kwargs_slicing(self):
        """Verify that surrogate_kwargs are correctly sliced per season."""
        # We'll use a mock to intercept the call to surrogate_test

        # Create a trend + season
        x = np.arange(24) + np.tile(np.array([10, -10]*6), 2)

        # Assume 2 seasons (odd/even months for simplicity of checking,
        # but here we use standard monthly so 12 seasons)

        # Let's use a simple numeric time with period=2 to have fewer seasons to check
        t_num = np.arange(24)
        period = 2

        # dy array matching original data
        dy_full = np.arange(24) * 0.1

        with patch('MannKS.seasonal_trend_test.surrogate_test') as mock_surr:
            # Mock return value to avoid AttributeError
            mock_res = MagicMock()
            mock_res.surrogate_scores = np.zeros(10)
            mock_res.notes = []
            mock_surr.return_value = mock_res

            seasonal_trend_test(
                x, t_num, period=period,
                surrogate_method='iaaft',
                n_surrogates=10,
                surrogate_kwargs={'dy': dy_full}
            )

            # Check calls
            # Should be called for each season (0 and 1)
            # Season 0 indices: 0, 2, 4, ...
            # Season 1 indices: 1, 3, 5, ...

            assert mock_surr.call_count == 2

            # Check arguments for first call (Season 0)
            args, kwargs = mock_surr.call_args_list[0]

            # Expected dy for season 0
            expected_dy_s0 = dy_full[::2]

            assert 'dy' in kwargs
            np.testing.assert_array_equal(kwargs['dy'], expected_dy_s0)

    def test_power_test_invalid_slope_scaling(self):
        """Test power_test with invalid slope scaling unit."""
        x = np.random.randn(50)
        t = np.arange(50)
        slopes = [0.1]

        with pytest.raises(ValueError, match="Invalid `slope_scaling` parameter"):
            power_test(x, t, slopes, slope_scaling='invalid_unit', n_simulations=5)

    def test_power_test_detrend(self):
        """Test that detrend=True actually changes the noise model."""
        # Create data with a HUGE trend.
        # If detrend=False, the surrogates will preserve this trend's low freq power,
        # making it hard to detect a small added trend (power should be low).
        # If detrend=True, the trend is removed, surrogates are flatter,
        # making it easier to detect the added trend (power should be higher).

        t = np.arange(100)
        # Strong trend
        x = t * 10.0 + np.random.randn(100)

        # Small slope to test
        slopes = [0.5]

        # Run with detrend=False
        res_no_detrend = power_test(
            x, t, slopes,
            n_simulations=50, n_surrogates=50,
            detrend=False, random_state=42
        )

        # Run with detrend=True
        res_detrend = power_test(
            x, t, slopes,
            n_simulations=50, n_surrogates=50,
            detrend=True, random_state=42
        )

        # We expect higher power with detrending because the background noise variance
        # (estimated from residuals) will be much lower than variance of raw trended data.
        # Wait, IAAFT/LombScargle preserves power spectrum.
        # A linear trend looks like infinite low-frequency power.
        # Surrogates will have huge low-frequency waves.
        # Adding a small linear trend to that might be insignificant.

        # With detrend=True, we remove the trend. The residuals are white-ish noise.
        # Surrogates will be white-ish.
        # Adding a small linear trend to white noise should be detectable.

        print(f"Power (No Detrend): {res_no_detrend.power[0]}")
        print(f"Power (Detrend): {res_detrend.power[0]}")

        assert res_detrend.power[0] >= res_no_detrend.power[0]

    def test_seasonal_trend_test_surrogate_kwargs_mismatch_error(self):
        """Test that a mismatch in surrogate kwargs raises ValueError when aggregation is used."""
        # Create data with 2 points per month to force ACTUAL aggregation
        t = pd.date_range(start='2020-01-01', periods=24, freq='ME')
        t = np.repeat(t, 2) # 48 points
        x = np.random.randn(48)

        # Aggregation enabled
        agg_method = 'median'

        # Kwargs that matches original length
        dy_full = np.ones(48)

        # Expected behavior: ValueError because we can't map dy_full to aggregated data safely
        # without original_index (which 'median' aggregation drops).

        with pytest.raises(ValueError, match="cannot be automatically mapped"):
            seasonal_trend_test(
                x, t, period=12,
                agg_method=agg_method,
                surrogate_method='iaaft',
                surrogate_kwargs={'dy': dy_full}
            )
