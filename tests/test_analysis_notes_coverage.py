"""
Tests for analysis_notes.py to improve test coverage.
"""
import unittest
import pandas as pd
import numpy as np
from MannKenSen.analysis_notes import get_analysis_note, get_sens_slope_analysis_note

class TestAnalysisNotesCoverage(unittest.TestCase):

    def test_get_analysis_note_all_na(self):
        """Test the case where all values are NA."""
        data = pd.DataFrame({
            'value': [np.nan, np.nan, np.nan],
            'censored': [False, False, False]
        })
        note = get_analysis_note(data)
        self.assertEqual(note, "Data all NA values")

    def test_get_analysis_note_seasonal_no_season_col(self):
        """Test seasonal post-aggregation check with no season column."""
        data = pd.DataFrame({
            'value': [1, 2, 3],
            'censored': [False, False, False]
        })
        note = get_analysis_note(data, is_seasonal=True, post_aggregation=True)
        self.assertEqual(note, "ok")

    def test_get_analysis_note_insufficient_non_na_in_season(self):
        """Test for < 3 non-NA values in a season."""
        data = pd.DataFrame({
            'value': [1, 2, 3, 4, 5, 6],
            'censored': [False] * 6,
            'season': ['Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2']
        })
        note = get_analysis_note(data, is_seasonal=True, post_aggregation=True)
        self.assertEqual(note, "< 3 non-NA values in Season")

    def test_get_analysis_note_long_run_in_season(self):
        """Test for a long run of a single value in a season."""
        data = pd.DataFrame({
            'value': [1, 1, 1, 1, 2, 5, 6, 7, 8],
            'censored': [False] * 9,
            'season': ['Q1', 'Q1', 'Q1', 'Q1', 'Q1', 'Q2', 'Q2', 'Q2', 'Q2']
        })
        note = get_analysis_note(data, is_seasonal=True, post_aggregation=True)
        self.assertEqual(note, "Long run of single value in a Season")

    def test_get_sens_slope_analysis_note_no_slopes(self):
        """Test with None or empty slopes array."""
        self.assertEqual(get_sens_slope_analysis_note(None, [], []), "ok")
        self.assertEqual(get_sens_slope_analysis_note(np.array([]), [], []), "ok")

    def test_get_sens_slope_analysis_note_nan_median(self):
        """Test with a slopes array that has a NaN median."""
        slopes = np.array([1, 2, np.nan])
        t = np.arange(3)
        cen_type = np.array(['not', 'not', 'not'])
        self.assertEqual(get_sens_slope_analysis_note(slopes, t, cen_type), "ok")

    def test_get_sens_slope_analysis_note_mismatched_lengths(self):
        """Test with mismatched lengths of slopes and valid time diffs."""
        slopes = np.array([1, 2, 3])
        t = np.array([1, 1, 2, 3]) # This will create 5 valid diffs, not 3
        cen_type = np.array(['not'] * 4)
        note = get_sens_slope_analysis_note(slopes, t, cen_type)
        self.assertEqual(note, "ok")

    def test_get_sens_slope_analysis_note_two_censored(self):
        """Test where the Sen slope is based on two censored values."""
        slopes = np.array([0, 1, 2])
        t = np.array([1, 2, 3])
        # This setup creates 3 pairs: (0,1), (0,2), (1,2)
        # cen_type_pairs will be: 'lt lt', 'lt not', 'lt not'
        # If slopes are [0, 1, 2], median is 1. The cen_type_pair for the
        # median slope at index 1 will be 'lt not'. We need the median to be
        # from an 'lt lt' pair.
        slopes = np.array([1, 0, 2]) # median is 1, from pair 'lt lt'
        t = np.array([1, 2, 3, 4])
        # Manually create the inputs to force the condition
        i, j = np.triu_indices(4, k=1)
        t_diff = t[j] - t[i]
        valid_mask = t_diff != 0
        cen_type = np.array(['lt', 'lt', 'not', 'not'])
        cen_type_pairs = (cen_type[i] + " " + cen_type[j])[valid_mask]

        # Craft slopes so the median corresponds to an 'lt lt' pair
        slopes = np.arange(len(cen_type_pairs))
        median_slope = np.median(slopes)

        # Find index of a an 'lt lt' pair
        lt_lt_idx = np.where(cen_type_pairs == 'lt lt')[0][0]

        # Swap values to make the median fall on the 'lt lt' pair
        median_idx = np.argmin(np.abs(slopes - median_slope))
        slopes[lt_lt_idx], slopes[median_idx] = slopes[median_idx], slopes[lt_lt_idx]

        note = get_sens_slope_analysis_note(slopes, t, cen_type)
        self.assertIn("influenced by", note)

if __name__ == '__main__':
    unittest.main()
