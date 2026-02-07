
import pytest
import numpy as np
import pandas as pd
import warnings
from unittest.mock import patch

from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test
from MannKS.power import power_test, PowerResult
from MannKS._surrogate import surrogate_test, _iaaft_surrogates, _lomb_scargle_surrogates

class TestSurrogateAdversarial:
    """
    Adversarial tests for surrogate data generation and testing.
    Focus on extreme edge cases, invalid inputs, and stability.
    """

    def test_surrogate_all_nans(self):
        """Test surrogate_test with all-NaN input."""
        x = np.full(100, np.nan)
        t = np.arange(100)

        # Direct call to surrogate_test
        try:
            res = surrogate_test(x, t, n_surrogates=10)
        except ValueError as e:
            # Now we expect "Input `x` contains NaNs..."
            assert "Input `x` contains NaNs" in str(e)
        except Exception as e:
            pytest.fail(f"Crashed on all-NaN input: {e}")

    def test_surrogate_constant_data(self):
        """Test surrogate_test with constant data (variance=0)."""
        x = np.ones(50)
        t = np.arange(50)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res_iaaft = surrogate_test(x, t, method='iaaft', n_surrogates=10)
            assert res_iaaft.p_value >= 0
            assert np.allclose(res_iaaft.surrogate_scores, 0) # S should be 0 for constant data

            if _lomb_scargle_surrogates.__module__: # check if astropy loaded
                res_ls = surrogate_test(x, t, method='lomb_scargle', n_surrogates=10)
                assert res_ls.p_value >= 0
                assert np.allclose(res_ls.surrogate_scores, 0)

    def test_surrogate_tiny_sample(self):
        """Test with N=2 or N=3."""
        x = np.random.randn(3)
        t = np.arange(3)

        res = surrogate_test(x, t, n_surrogates=5)
        assert res.p_value >= 0
        assert len(res.surrogate_scores) == 5

    def test_surrogate_infinite_values(self):
        """Test with Inf values."""
        x = np.random.randn(50)
        x[10] = np.inf
        t = np.arange(50)

        try:
            res = surrogate_test(x, t, n_surrogates=10)
        except ValueError as e:
            assert "Input `x` contains NaNs or infinite values" in str(e)
        except Exception as e:
             pytest.fail(f"Crashed on Inf input: {e}")

    def test_surrogate_extreme_values(self):
        """Test with extremely large values (float overflow potential)."""
        x = np.random.randn(50) * 1e30
        t = np.arange(50)

        res = surrogate_test(x, t, n_surrogates=10)
        assert res.p_value >= 0

class TestPowerAdversarial:
    """
    Adversarial tests for power_test.
    """

    def test_power_invalid_simulations(self):
        """Test with invalid n_simulations."""
        x = np.random.randn(50)
        t = np.arange(50)

        try:
            power_test(x, t, slopes=[0.1], n_simulations=0)
            pytest.fail("Should have raised ValueError for n_simulations=0")
        except (ValueError, ZeroDivisionError):
            pass # Expected behavior? Or maybe it just returns empty result?
        except Exception as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_power_empty_slopes(self):
        """Test with empty slopes list."""
        x = np.random.randn(50)
        t = np.arange(50)

        res = power_test(x, t, slopes=[], n_simulations=5)
        assert len(res.power) == 0
        assert np.isnan(res.min_detectable_trend)

    def test_power_nan_slopes(self):
        """Test with NaNs in slopes."""
        x = np.random.randn(50)
        t = np.arange(50)

        res = power_test(x, t, slopes=[0.1, np.nan, 0.2], n_simulations=5)
        assert len(res.power) == 3
        assert np.isnan(res.power[1])

    def test_power_scaling_invalid(self):
        """Test with invalid slope_scaling string."""
        x = np.random.randn(50)
        t = pd.date_range('2020-01-01', periods=50, freq='D')

        try:
            power_test(x, t, slopes=[0.1], slope_scaling='invalid_unit')
            pytest.fail("Should have raised ValueError for invalid slope_scaling")
        except ValueError as e:
            assert "Invalid `slope_scaling`" in str(e)

class TestSeasonalAdversarial:
    """
    Adversarial tests for seasonal_trend_test.
    """

    def test_seasonal_surrogate_mismatch_length(self):
        """Test with surrogate kwarg that matches neither raw nor filtered length."""
        # Setup: 2 years of monthly data (24 points)
        t = pd.date_range('2020-01-01', periods=24, freq='ME')
        x = np.random.randn(24)

        # Make one point NaN to ensure filtered length != raw length
        x[0] = np.nan
        # Raw = 24, Filtered = 23

        # Pass a kwarg of length 10 (random mismatch)
        dy = np.ones(10)

        # Correct regex (relaxed to substring match)
        with pytest.raises(ValueError, match="match the original data length"):
             seasonal_trend_test(x, t, period=12, surrogate_method='auto', surrogate_kwargs={'dy': dy})

    def test_seasonal_aggressive_aggregation(self):
        """Test aggregation that results in single point per season."""
        # This is valid if no conflict
        t = pd.date_range('2020-01-01', periods=24, freq='ME')
        x = np.random.randn(24)
        res = seasonal_trend_test(x, t, period=12, agg_method='median')
        assert res.trend in ['increasing', 'decreasing', 'no trend']

    def test_seasonal_surrogate_agg_conflict(self):
        """
        Test providing array-like surrogate args when aggregation is used
        (which destroys the index mapping).
        """
        # Create data with multiple points per month (daily data for 2 years)
        # This ensures aggregation (median of month) actually reduces N
        t = pd.date_range('2020-01-01', periods=730, freq='D')
        x = np.random.randn(730)

        # Use agg_method='median' (triggers aggregation)
        # Pass dy with length 730 (matches original)
        # Since we aggregate to monthly, index is lost, and we can't map 730 error bars to 24 monthly points
        dy = np.ones(730)

        # Should raise ValueError because we can't map dy to the aggregated data automatically
        with pytest.raises(ValueError, match="cannot be automatically mapped"):
            seasonal_trend_test(
                x, t, period=12,
                agg_method='median',
                surrogate_method='auto',
                surrogate_kwargs={'dy': dy},
                season_type='month'
            )

if __name__ == "__main__":
    pytest.main([__file__])
