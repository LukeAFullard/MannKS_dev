
import numpy as np
import pytest
import warnings
from unittest.mock import MagicMock, patch
from MannKS.power import power_test
from MannKS.trend_test import trend_test
from MannKS.seasonal_trend_test import seasonal_trend_test

def test_power_test_kwargs_propagation():
    """Verify that kwargs passed to power_test are propagated to surrogate_test."""
    x = np.random.randn(50)
    t = np.arange(50)
    slopes = [0.1]

    # We want to check if 'censored' or 'dy' passed to power_test reaches surrogate_test.
    # We'll use a mock for surrogate_test.

    with patch('MannKS.power.surrogate_test') as mock_surrogate:
        # Mock return value to avoid AttributeError
        mock_result = MagicMock()
        mock_result.p_value = 0.01
        mock_result.method = 'iaaft'
        mock_surrogate.return_value = mock_result

        # Pass a specific kwarg 'my_custom_arg' which implies it should be in **kwargs
        # Also pass 'censored' which is important.
        custom_arg = "test_value"
        censored_arg = np.zeros(50, dtype=bool)

        power_test(x, t, slopes, n_simulations=2, n_surrogates=20,
                   my_custom_arg=custom_arg, censored=censored_arg)

        # Check call args
        assert mock_surrogate.called
        call_kwargs = mock_surrogate.call_args.kwargs

        # This assertion is expected to FAIL currently
        if 'my_custom_arg' not in call_kwargs:
            pytest.fail("kwargs were not propagated to surrogate_test!")

        assert call_kwargs['my_custom_arg'] == custom_arg
        assert 'censored' in call_kwargs

def test_seasonal_trend_test_kwargs_aggregation_error():
    """Verify ValueError is raised when aggregating with raw-length kwargs."""
    # Create data for 2 years, monthly
    t = np.arange(24)
    x = np.random.randn(24)
    dy = np.ones(24) * 0.1 # Error bars matching raw length

    # Aggregation: 'mean' (via agg_method='median' or similar? 'mean' is not valid for trend_test but valid for aggregation helpers?)
    # seasonal_trend_test supports 'median', 'lwp', etc.

    # We use 'median' aggregation. This will reduce data if we had multiple points per season-cycle.
    # Here we have 1 point per month. So length matches.
    # But seasonal_trend_test logic checks if we can map index.
    # If agg_method != 'none', it drops original_index (unless specifically preserved, which helper does NOT do for >1 agg).

    # To force mismatch or ambiguity, let's have 2 points per month.
    t_dup = np.repeat(np.arange(24), 2) # 48 points
    x_dup = np.random.randn(48)
    dy_dup = np.ones(48) # Matches raw length

    # Run with aggregation
    with pytest.raises(ValueError, match="cannot be automatically mapped"):
        seasonal_trend_test(
            x_dup, t_dup, period=12,
            agg_method='median',
            surrogate_method='auto',
            surrogate_kwargs={'dy': dy_dup}
        )

def test_trend_test_agg_mean_fail():
    """Verify trend_test fails with agg_method='mean'."""
    x = np.random.randn(20)
    t = np.arange(20)
    with pytest.raises(ValueError, match="Invalid `agg_method`"):
        trend_test(x, t, agg_method='mean')

def test_surrogate_test_constant_input():
    """Verify surrogate_test handles constant input without crashing."""
    x = np.ones(50)
    t = np.arange(50)

    # constants should produce constant surrogates (variance 0)
    # mk score should be 0

    from MannKS._surrogate import surrogate_test
    res = surrogate_test(x, t, method='lomb_scargle', n_surrogates=20)

    assert res.original_score == 0
    assert np.all(res.surrogate_scores == 0)
    # p-value might be 1.0 (all 0 >= 0)
    assert res.p_value == 1.0

if __name__ == "__main__":
    # Manually run tests if executed as script
    import sys
    sys.exit(pytest.main(["-v", __file__]))
