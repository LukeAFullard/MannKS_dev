# V-34: Seasonal Sensitivity Sweep

Verifies metrics for seasonal data with mixed censoring.

Total Tests: 8
Class Matches: 8 (100.0%)
Max Slope Diff: 0.000001
Max P-value Diff: 0.000000
Max Lower CI Diff: 0.027079
Max Upper CI Diff: 0.024357

|   slope_in |   censor_pct |   slope_diff |      p_diff |   lci_diff |   uci_diff | match_class   | py_class                    | r_class                     |
|-----------:|-------------:|-------------:|------------:|-----------:|-----------:|:--------------|:----------------------------|:----------------------------|
|        0   |          0   |  1.73472e-18 | 0           | 0.00592471 | 0.0152218  | True          | as likely as not decreasing | as likely as not decreasing |
|        0   |          0   |  0           | 0           | 0.0244391  | 0.00127335 | True          | as likely as not decreasing | as likely as not decreasing |
|        0   |          0.3 |  0           | 0           | 0.0270794  | 0.0131054  | True          | as likely as not increasing | as likely as not increasing |
|        0   |          0.3 |  6.93889e-18 | 5.55112e-17 | 0.00045992 | 0.013228   | True          | highly likely increasing    | highly likely increasing    |
|        0.2 |          0   |  2.77556e-17 | 3.46945e-18 | 0.00346979 | 0.0123079  | True          | highly likely increasing    | highly likely increasing    |
|        0.2 |          0   |  0           | 1.08583e-16 | 0.01192    | 0.00351941 | True          | highly likely increasing    | highly likely increasing    |
|        0.2 |          0.3 |  1.39332e-06 | 7.89299e-17 | 0.0123464  | 0.024357   | True          | highly likely increasing    | highly likely increasing    |
|        0.2 |          0.3 |  1.38778e-17 | 4.85723e-17 | 0.00660106 | 0.0104836  | True          | highly likely increasing    | highly likely increasing    |