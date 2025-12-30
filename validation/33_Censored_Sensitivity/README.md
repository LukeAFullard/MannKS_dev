# V-33: Censored Sensitivity Sweep (Non-Seasonal)

Verifies Sen's slope, p-value, CIs, and classification for non-seasonal data with mixed censoring.

Total Tests: 99
Class Matches: 99 (100.0%)
Max Slope Diff: 0.000027
Max P-value Diff: 0.009176
Max Lower CI Diff: 0.055813
Max Upper CI Diff: 0.091584

## Detailed Results (Top 20)
|   iter |   slope_in |   noise_in |   censor_pct |   slope_diff |      p_diff |   lci_diff |   uci_diff | match_class   | py_class                    | r_class                     |
|-------:|-----------:|-----------:|-------------:|-------------:|------------:|-----------:|-----------:|:--------------|:----------------------------|:----------------------------|
|      1 |       0    |   0.1      |          0.6 |  0           | 0.00127769  | 0          | 0          | True          | as likely as not increasing | as likely as not increasing |
|      2 |       0    |   1.02627  |          0.6 |  0           | 0.00284257  | 0          | 0          | True          | as likely as not increasing | as likely as not increasing |
|      3 |      -0.05 |   0.1      |          0.2 |  0           | 1.34821e-07 | 0.00356262 | 0.00289228 | True          | highly likely decreasing    | highly likely decreasing    |
|      4 |       0.1  |   1.97577  |          0.4 |  0           | 0.00248369  | 0          | 0.0498613  | True          | likely increasing           | likely increasing           |
|      5 |       0    |   2.00886  |          0.1 |  6.93889e-18 | 1.11022e-16 | 0.0540585  | 0.0588253  | True          | likely decreasing           | likely decreasing           |
|      6 |       0.1  |   0.105364 |          0.4 |  0           | 1.77228e-13 | 0.00309371 | 0.00290687 | True          | highly likely increasing    | highly likely increasing    |
|      7 |      -0.1  |   1.00569  |          0.2 |  0           | 2.33442e-05 | 0.0266081  | 0.02698    | True          | as likely as not decreasing | as likely as not decreasing |
|      8 |       0    |   1.04333  |          0.4 |  0           | 0.00116398  | 0          | 0.0281188  | True          | likely increasing           | likely increasing           |
|      9 |      -0.05 |   1.01374  |          0.3 |  0           | 0.0004819   | 0.0305058  | 0.0234049  | True          | as likely as not increasing | as likely as not increasing |
|     10 |       0.05 |   0.532122 |          0.2 |  0           | 0.00012435  | 0.0181561  | 0.00929934 | True          | likely increasing           | likely increasing           |
|     11 |       0.1  |   0.101259 |          0.6 |  3.65887e-08 | 1.62137e-10 | 0.00738358 | 0.00337671 | True          | highly likely increasing    | highly likely increasing    |
|     12 |      -0.1  |   0.500206 |          0.4 |  0           | 0.000922605 | 0.0150589  | 0          | True          | highly likely decreasing    | highly likely decreasing    |
|     13 |       0.05 |   1.97979  |          0.5 |  0           | 0.0025582   | 0          | 0.0915843  | True          | highly likely increasing    | highly likely increasing    |
|     14 |       0    |   0.549889 |          0.2 |  0           | 2.64188e-05 | 0.0124204  | 0.0167957  | True          | as likely as not increasing | as likely as not increasing |
|     15 |      -0.1  |   0.11531  |          0.4 |  5.55458e-07 | 1.19767e-11 | 0.00420323 | 0.00482234 | True          | highly likely decreasing    | highly likely decreasing    |
|     16 |       0    |   1.01053  |          0.5 |  0           | 0.00317373  | 0          | 0.0303238  | True          | likely increasing           | likely increasing           |
|     17 |      -0.1  |   0.523831 |          0.2 |  5.73917e-07 | 0.000704768 | 0.0132019  | 0.0103426  | True          | likely increasing           | likely increasing           |
|     18 |       0.05 |   0.144574 |          0.6 |  3.46945e-18 | 2.69506e-05 | 0          | 0.00508128 | True          | highly likely increasing    | highly likely increasing    |
|     19 |       0.1  |   0.965414 |          0.5 |  0           | 0.00201636  | 0          | 0.0242847  | True          | likely increasing           | likely increasing           |
|     20 |      -0.05 |   0.471677 |          0.5 |  0           | 0.00256304  | 0.00963109 | 0          | True          | likely decreasing           | likely decreasing           |