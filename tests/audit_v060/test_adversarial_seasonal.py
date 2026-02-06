
import pytest
import numpy as np
import pandas as pd
from MannKS.seasonal_trend_test import seasonal_trend_test

class TestAdversarialSeasonal:
    """
    Adversarial tests for Seasonal Integration in v0.6.0.
    Focus on data misalignment and argument conflicts.
    """

    def test_agg_median_surrogate_kwargs_conflict(self):
        """
        Test Conflict: Aggregation (median) + Array-like Surrogate Kwargs.

        Scenario:
        - Input: 100 days of data.
        - Aggregation: 'median' to monthly (approx 3 points).
        - Surrogate Kwargs: 'dy' with 100 points (original errors).

        Issue: 'median' aggregation destroys the 1-to-1 mapping or original index.
        The system cannot know which 'dy' value corresponds to the median'd value
        (it's a statistic, not a specific point).

        Expected: ValueError explaining that kwargs cannot be mapped when aggregation is used.
        """
        # Generate daily data for 2+ years so each season has >1 point
        # Otherwise the loop skips the season and the check is never reached.
        dates = pd.date_range(start='2020-01-01', periods=750, freq='D')
        values = np.random.randn(750)
        errors = np.ones(750) * 0.1 # Array-like matching original length

        # We expect a ValueError because 'median' aggregation is requested
        # AND an array-like surrogate kwarg ('dy') is provided.
        with pytest.raises(ValueError, match="Surrogate arguments .* cannot be automatically mapped"):
            seasonal_trend_test(
                values, dates,
                agg_method='median',
                agg_period='month',
                season_type='month',
                surrogate_method='lomb_scargle', # Needs dy usually, but checking mapping logic
                surrogate_kwargs={'dy': errors},
                n_surrogates=10
            )

    def test_agg_middle_surrogate_kwargs_success(self):
        """
        Test Success: Aggregation (middle) + Array-like Surrogate Kwargs.

        Scenario:
        - Input: 90 days.
        - Aggregation: 'middle' selects ONE row per group. Preserves 'original_index'.
        - Surrogate Kwargs: 'dy' with 90 points.

        Expected: Success. The system should use 'original_index' to pick the correct 'dy'.
        """
        dates = pd.date_range(start='2020-01-01', periods=90, freq='D')
        values = np.random.randn(90)
        errors = np.ones(90) * 0.1

        # Should NOT raise
        res = seasonal_trend_test(
            values, dates,
            agg_method='middle', # Preserves index
            agg_period='month',
            season_type='month',
            surrogate_method='lomb_scargle',
            surrogate_kwargs={'dy': errors},
            n_surrogates=10
        )
        assert res.trend is not None

    def test_agg_none_surrogate_kwargs_success(self):
        """
        Test Success: No Aggregation + Array-like Surrogate Kwargs.

        Scenario: Standard usage.
        Expected: Success.
        """
        dates = pd.date_range(start='2020-01-01', periods=24, freq='ME') # Monthly data
        values = np.random.randn(24)
        errors = np.ones(24) * 0.1

        res = seasonal_trend_test(
            values, dates,
            agg_method='none',
            season_type='month',
            surrogate_method='lomb_scargle',
            surrogate_kwargs={'dy': errors},
            n_surrogates=10
        )
        assert res.trend is not None

    def test_surrogate_kwargs_length_mismatch(self):
        """
        Test Mismatch: 'dy' has wrong length (not N_raw and not N_filtered).
        Expected: ValueError or passing it through (which then fails in surrogate_test or astropy).
        Wait, logic says "if len != n_raw ... else kwargs[k] = v".
        So it passes it through. Astropy might raise.
        """
        dates = pd.date_range(start='2020-01-01', periods=10, freq='D')
        values = np.random.randn(10)
        errors = np.ones(5) # Wrong length

        # The seasonal test splits data by season.
        # If we pass a 5-element array, it won't match n_raw (10).
        # It won't match n_filtered (10).
        # It gets passed as-is to each season.
        # Season 1 (Jan) might have 10 points.
        # Surrogate test gets x (10) and dy (5).
        # Lomb-Scargle should raise ValueError.

        with pytest.raises(ValueError):
             seasonal_trend_test(
                values, dates,
                surrogate_method='lomb_scargle',
                surrogate_kwargs={'dy': errors},
                n_surrogates=5
            )
