
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock
from MannKS.seasonal_trend_test import seasonal_trend_test

def test_seasonal_surrogate_kwargs_alignment():
    """
    Verify correct slicing of array-like surrogate_kwargs in seasonal test (no aggregation).
    """
    # 2 Years of Monthly data (24 points)
    t = pd.date_range(start='2020-01-01', periods=24, freq='ME')
    x = np.random.randn(24)
    # Error array corresponding to each point
    dy = np.arange(24)

    # We want to ensure that when Month 1 (January) is processed,
    # the 'dy' passed to surrogate_test matches the indices [0, 12].

    with patch('MannKS.seasonal_trend_test.surrogate_test') as mock_surr:
        # Mock return
        mock_surr.return_value = MagicMock(
            surrogate_scores=np.zeros(10), p_value=0.5, z_score=0, notes=[]
        )

        seasonal_trend_test(
            x, t,
            surrogate_method='iaaft', n_surrogates=10,
            surrogate_kwargs={'dy': dy},
            agg_method='none' # No aggregation
        )

        # Verify calls
        # There should be 12 calls (one per season)
        assert mock_surr.call_count == 12

        # Check January (Season 1)
        # In pandas month is 1-based.
        # Indices for Jan: 0 (Jan 2020), 12 (Jan 2021)
        # Expected dy: [0, 12]

        # We need to find which call corresponded to January.
        # The loop order in seasonal_trend_test depends on season_range.
        # Usually 1..12.

        # Let's inspect all calls and verify that for every call,
        # the passed 'x' and 'dy' match.

        for args, kwargs in mock_surr.call_args_list:
            x_arg = kwargs['x'] # Passed as keyword argument
            dy_arg = kwargs['dy']

            # They must be same length
            assert len(x_arg) == len(dy_arg)

            # And values must correspond to the original alignment
            # We can recover the indices from the values of dy (since dy = indices)
            indices = dy_arg
            if isinstance(x, pd.Series) or isinstance(x, np.ndarray):
                x_vals = np.array(x)
                expected_x = x_vals[indices]
                np.testing.assert_array_equal(x_arg, expected_x)

def test_seasonal_aggregation_error():
    """
    Verify ValueError when passing raw-length kwargs with aggregation.
    """
    # Daily data, aggregating to Monthly. Need >1 year to trigger seasonal logic.
    t = pd.date_range(start='2020-01-01', periods=400, freq='D') # > 1 year
    x = np.random.randn(400)
    dy = np.random.randn(400) # Matches raw length

    with pytest.raises(ValueError, match="cannot be automatically mapped"):
        seasonal_trend_test(
            x, t,
            agg_method='median', # Aggregation (median)
            agg_period='month',
            surrogate_method='iaaft',
            surrogate_kwargs={'dy': dy}
        )
