"""
Tests for the regional_test function.
"""
import unittest
import pandas as pd
import numpy as np
from MannKenSen import original_test, regional_test

class TestRegionalAggregation(unittest.TestCase):
    def test_regional_test_basic(self):
        """
        Test the regional_test function with a synthetic dataset.
        """
        # --- 1. Create Synthetic Data ---
        # Three sites: A is increasing, B is decreasing, C is increasing
        dates = pd.to_datetime(pd.date_range(start='2000-01-01', periods=20, freq='YE'))
        sites = ['A', 'B', 'C']
        all_ts_data = []

        for site in sites:
            np.random.seed(hash(site) % (2**32 - 1))
            noise = np.random.normal(0, 1.0, 20)
            if site == 'B':
                trend = -0.1 * np.arange(20)
            else:
                trend = 0.1 * np.arange(20)

            values = 10 + trend + noise

            df = pd.DataFrame({
                'time': dates,
                'value': values,
                'site': site
            })
            all_ts_data.append(df)

        time_series_data = pd.concat(all_ts_data, ignore_index=True)

        # --- 2. Run Single-Site Trend Analysis ---
        trend_results = []
        for site in sites:
            site_data = time_series_data[time_series_data['site'] == site]
            res = original_test(x=site_data['value'], t=site_data['time'])

            # Convert namedtuple to a dictionary and add site
            res_dict = res._asdict()
            res_dict['site'] = site
            trend_results.append(res_dict)

        trend_results_df = pd.DataFrame(trend_results)

        # --- 3. Run Regional Trend Aggregation ---
        regional_res = regional_test(trend_results=trend_results_df,
                                     time_series_data=time_series_data,
                                     site_col='site',
                                     value_col='value',
                                     time_col='time',
                                     s_col='s',
                                     c_col='C')

        # --- 4. Assertions ---
        self.assertIsInstance(regional_res, tuple)
        self.assertEqual(regional_res.M, 3)

        # Modal direction should be 'Increasing' (2 of 3 sites are increasing)
        self.assertEqual(regional_res.DT, 'Increasing')

        # TAU should be 2/3
        self.assertAlmostEqual(regional_res.TAU, 2/3, places=5)

        # Check that variances and confidence are plausible floats
        self.assertIsInstance(regional_res.VarTAU, float)
        self.assertIsInstance(regional_res.CorrectedVarTAU, float)
        self.assertIsInstance(regional_res.CT, float)

        # Corrected variance should be different from uncorrected
        self.assertNotAlmostEqual(regional_res.VarTAU, regional_res.CorrectedVarTAU)

if __name__ == '__main__':
    unittest.main()
