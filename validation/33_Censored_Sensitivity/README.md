# V-33: Censored Sensitivity Sweep (Non-Seasonal)

Verifies Sen's slope, p-value, CIs, and classification for non-seasonal data with mixed censoring.

Total Tests: 36
Class Matches: 35 (97.2%)
Max Slope Diff: 0.000007
Max P-value Diff: 0.010695
Max Lower CI Diff: 0.037025
Max Upper CI Diff: 0.031707

## Detailed Results (Top 20)
|   slope_in |   noise_in |   censor_pct |   slope_diff |      p_diff |   lci_diff |   uci_diff | match_class   | py_class                    | r_class                        |
|-----------:|-----------:|-------------:|-------------:|------------:|-----------:|-----------:|:--------------|:----------------------------|:-------------------------------|
|        0   |        0.5 |          0.2 |  0           | 0.000110305 | 0.00838379 |  0.0100887 | True          | likely increasing           | likely increasing              |
|        0   |        0.5 |          0.2 |  2.6812e-06  | 0.000415729 | 0.0143349  |  0.0110058 | True          | as likely as not decreasing | as likely as not decreasing    |
|        0   |        0.5 |          0.2 |  5.71181e-06 | 0.000195762 | 0          |  0.0192525 | True          | highly likely increasing    | highly likely increasing       |
|        0   |        0.5 |          0.5 |  0           | 0.000905392 | 0          |  0.012443  | True          | as likely as not increasing | as likely as not increasing    |
|        0   |        0.5 |          0.5 |  0           | 0.0106951   | 0.0139143  |  0         | True          | likely decreasing           | likely decreasing              |
|        0   |        0.5 |          0.5 |  0           | 0.00317373  | 0          |  0.0150093 | True          | likely increasing           | likely increasing              |
|        0   |        1   |          0.2 |  0           | 2.59072e-05 | 0.0326639  |  0.0317073 | True          | as likely as not increasing | as likely as not increasing    |
|        0   |        1   |          0.2 |  0           | 1.05679e-05 | 0.0259469  |  0.0251414 | True          | as likely as not decreasing | as likely as not decreasing    |
|        0   |        1   |          0.2 |  0           | 0.000258194 | 0.0370249  |  0.0198931 | True          | likely decreasing           | likely decreasing              |
|        0   |        1   |          0.5 |  0           | 0.00214313  | 0.0335429  |  0         | True          | as likely as not decreasing | as likely as not decreasing    |
|        0   |        1   |          0.5 |  0           | 0.00394591  | 0.0262897  |  0         | True          | likely decreasing           | likely decreasing              |
|        0   |        1   |          0.5 |  0           | 0           | 0          |  0         | False         | as likely as not no trend   | as likely as not indeterminate |
|        0.1 |        0.5 |          0.2 |  0           | 0.00020092  | 0.0116661  |  0.0141473 | True          | highly likely increasing    | highly likely increasing       |
|        0.1 |        0.5 |          0.2 |  6.93889e-18 | 7.5086e-05  | 0.00698431 |  0.0096946 | True          | highly likely increasing    | highly likely increasing       |
|        0.1 |        0.5 |          0.2 |  0           | 0.00083322  | 0.00931062 |  0.0204473 | True          | likely increasing           | likely increasing              |
|        0.1 |        0.5 |          0.5 |  0           | 0.00931104  | 0          |  0.0212493 | True          | likely increasing           | likely increasing              |
|        0.1 |        0.5 |          0.5 |  1.38778e-17 | 6.32155e-05 | 0          |  0.0138161 | True          | highly likely increasing    | highly likely increasing       |
|        0.1 |        0.5 |          0.5 |  0           | 0.000802942 | 0          |  0.0164383 | True          | highly likely increasing    | highly likely increasing       |
|        0.1 |        1   |          0.2 |  1.38778e-17 | 6.89999e-05 | 0.0098387  |  0.0202383 | True          | highly likely increasing    | highly likely increasing       |
|        0.1 |        1   |          0.2 |  2.31214e-06 | 0.000225708 | 0.022156   |  0.0297101 | True          | likely decreasing           | likely decreasing              |