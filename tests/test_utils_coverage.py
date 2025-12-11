"""
Tests for _utils.py to improve test coverage.
"""
import unittest
import pandas as pd
import numpy as np
from MannKenSen._utils import (_is_datetime_like, _get_season_func,
                             _get_cycle_identifier, _rle_lengths,
                             __missing_values_analysis,
                             _mk_score_and_var_censored)

class TestUtilsCoverage(unittest.TestCase):

    def test_get_season_func_invalid_season(self):
        """Test _get_season_func with an invalid season_type."""
        with self.assertRaises(ValueError):
            _get_season_func('invalid_season', 12)

    def test_get_season_func_invalid_period(self):
        """Test _get_season_func with an invalid period for a given season_type."""
        with self.assertRaises(ValueError):
            _get_season_func('month', 13)
        with self.assertRaises(ValueError):
            _get_season_func('week_of_year', 51)

    def test_rle_lengths_empty_input(self):
        """Test _rle_lengths with an empty array."""
        self.assertEqual(len(_rle_lengths(np.array([]))), 0)

    def test_get_cycle_identifier_edge_cases(self):
        """Test _get_cycle_identifier with less common season types."""
        dates = pd.to_datetime(pd.date_range(start='2023-01-01', periods=5, freq='D'))

        # Test day_of_week
        cycles_dow = _get_cycle_identifier(dates, 'day_of_week')
        self.assertEqual(len(cycles_dow), 5)

        # Test hour, minute, second
        dates_hourly = pd.to_datetime(pd.date_range(start='2023-01-01', periods=5, freq='h'))
        cycles_hour = _get_cycle_identifier(dates_hourly, 'hour')
        self.assertEqual(len(np.unique(cycles_hour)), 1) # All on the same day

    def test_mk_score_and_var_censored_no_variance(self):
        """Test _mk_score_and_var_censored with data that has no variance."""
        x = np.array([5, 5, 5])
        t = np.array([1, 2, 3])
        censored = np.array([False, False, False])
        cen_type = np.array(['not', 'not', 'not'])
        s, var_s, D = _mk_score_and_var_censored(x, t, censored, cen_type)
        self.assertEqual(s, 0)
        self.assertGreaterEqual(var_s, 0)
        self.assertEqual(D, 3)

if __name__ == '__main__':
    unittest.main()
