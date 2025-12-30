# V-34: Seasonal Sensitivity Sweep

Verifies metrics for seasonal data with mixed censoring.

Total Tests: 99
Class Matches: 96 (97.0%)
Max Slope Diff: 0.000014
Max P-value Diff: 0.005821
Max Lower CI Diff: 0.087159
Max Upper CI Diff: 0.116818

|   iter |   slope_in |   censor_pct |   slope_diff |      p_diff |   lci_diff |   uci_diff | match_class   | py_class                    | r_class                     |
|-------:|-----------:|-------------:|-------------:|------------:|-----------:|-----------:|:--------------|:----------------------------|:----------------------------|
|      1 |       0    |          0.2 |  0           | 0.00582103  | 0.00196226 | 0.00199293 | True          | as likely as not increasing | as likely as not increasing |
|      2 |       0    |          0.1 |  1.73472e-18 | 0.00132473  | 0.0253172  | 0.0128942  | True          | as likely as not decreasing | as likely as not decreasing |
|      3 |       0.15 |          0.1 |  0           | 6.24618e-17 | 0.00554683 | 0.00114568 | True          | highly likely increasing    | highly likely increasing    |
|      4 |       0.1  |          0.3 |  0           | 2.77556e-17 | 0.00543676 | 0.0176846  | True          | very likely increasing      | very likely increasing      |
|      5 |       0    |          0   |  6.93889e-18 | 0           | 0.027822   | 0.106575   | True          | likely decreasing           | likely decreasing           |
|      6 |       0.1  |          0.3 |  1.38778e-17 | 2.8386e-17  | 0.00814002 | 0.00156563 | True          | highly likely increasing    | highly likely increasing    |
|      7 |       0.2  |          0.1 |  5.55112e-17 | 1.38778e-16 | 0.0611435  | 0.0220645  | True          | highly likely increasing    | highly likely increasing    |
|      8 |       0    |          0.3 |  8.92809e-06 | 0.00192418  | 0.01023    | 0.0374371  | True          | likely increasing           | likely increasing           |
|      9 |       0.15 |          0.2 |  1.38778e-17 | 9.71445e-17 | 0          | 0.0335094  | True          | very likely increasing      | very likely increasing      |
|     10 |       0.05 |          0.1 |  0           | 0           | 0.0165985  | 0.0137285  | True          | as likely as not decreasing | as likely as not decreasing |
|     11 |       0.1  |          0.4 |  0           | 2.01907e-17 | 0.00508504 | 0.00272665 | True          | highly likely increasing    | highly likely increasing    |
|     12 |       0.2  |          0.3 |  2.24778e-06 | 3.90313e-17 | 0.0236092  | 0.0344518  | True          | highly likely increasing    | highly likely increasing    |
|     13 |       0.05 |          0.4 |  2.77556e-17 | 7.63278e-17 | 0          | 0.035975   | True          | highly likely increasing    | highly likely increasing    |
|     14 |       0    |          0.1 |  0           | 1.11022e-16 | 0.0128444  | 0.00698034 | True          | as likely as not increasing | as likely as not increasing |
|     15 |       0.2  |          0.3 |  0           | 1.00683e-16 | 0.00350136 | 0.00712459 | True          | highly likely increasing    | highly likely increasing    |
|     16 |       0    |          0.4 |  0           | 2.22045e-16 | 0.0871587  | 0.049912   | True          | likely increasing           | likely increasing           |
|     17 |       0.2  |          0.1 |  0           | 9.66973e-17 | 0.0111675  | 0.0184025  | True          | highly likely increasing    | highly likely increasing    |
|     18 |       0.05 |          0.3 |  6.93889e-18 | 3.99504e-08 | 0.00486145 | 0.0025655  | True          | highly likely increasing    | highly likely increasing    |
|     19 |       0.1  |          0.4 |  1.44034e-05 | 1.11022e-16 | 0.00987565 | 0.0342868  | True          | likely increasing           | likely increasing           |
|     20 |       0.15 |          0.4 |  0           | 8.19657e-17 | 0.0115075  | 0.0248937  | True          | highly likely increasing    | highly likely increasing    |