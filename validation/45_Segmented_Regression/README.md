# Validation Report: Segmented Regression

| ID | Description | Success | Result |
|---|---|---|---|
| V-45-01 | No Breakpoint (Linear Trend) | PASS | 0 |
| V-45-02 | Single Hinge Detection (True BP=50) | PASS | 1 |
| V-45-03 | Censored Hinge (Robustness) | PASS | 2 |
| V-45-04 | Double Jump (True BPs=30, 70) | PASS | 2 |
| V-45-05 | Probability Calibration (True BP=50, Window=[45, 55]) | PASS | Probability: 84.00% |


## Detailed Results

### V-45-01: No Breakpoint (Linear Trend)
**Success:** True

#### Model Selection Summary
|   n_breakpoints |      bic |     sar | converged   |
|----------------:|---------:|--------:|:------------|
|               0 | -93.0995 | 35.9479 | True        |
|               1 | -83.492  | 34.4666 | True        |
|               2 | -71.3692 | 33.8881 | True        |

![Plot](v45_01_plot.png)

### V-45-02: Single Hinge Detection (True BP=50)
**Success:** True

#### Model Selection Summary
|   n_breakpoints |      bic |      sar | converged   |
|----------------:|---------:|---------:|:------------|
|               0 |  74.8933 | 192.867  | True        |
|               1 | -80.413  |  35.5444 | True        |
|               2 | -69.9952 |  34.357  | True        |

**Detected Breakpoint:** 49.011111111111106

![Plot](v45_02_plot.png)

### V-45-03: Censored Hinge (Robustness)
**Success:** True

#### Model Selection Summary
|   n_breakpoints |       bic |     sar | converged   |
|----------------:|----------:|--------:|:------------|
|               0 |  -26.7649 | 69.7849 | True        |
|               1 |  -78.7251 | 36.1494 | True        |
|               2 | -102.009  | 24.9449 | True        |

![Plot](v45_03_plot.png)

### V-45-04: Double Jump (True BPs=30, 70)
**Success:** True

#### Model Selection Summary
|   n_breakpoints |      bic |      sar | converged   |
|----------------:|---------:|---------:|:------------|
|               0 |  29.467  | 122.454  | True        |
|               1 |  21.2381 |  98.2281 | True        |
|               2 | -68.976  |  34.7089 | True        |
|               3 | -59.3955 |  33.2697 | True        |

![Plot](v45_04_plot.png)

### V-45-05: Probability Calibration (True BP=50, Window=[45, 55])
**Success:** True

**Metric:** Probability: 84.00%
