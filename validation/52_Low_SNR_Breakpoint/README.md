# Validation 52: Low SNR Breakpoint Detection

Comparision across 100 random datasets (Non-censored, Low SNR, Sigma=5.0) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 40.0% |
| MannKS (Standard AIC) | 50.0% |
| MannKS (Merged) | 50.0% |
| **MannKS (Bagging)** | **45.0%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   -1 |   0 |   1 |   2 |
|---------:|-----:|----:|----:|----:|
|        0 |    8 |  17 |   0 |   0 |
|        1 |    8 |  10 |  22 |   2 |
|        2 |    3 |   7 |  22 |   1 |

#### MannKS (Standard AIC)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |  18 |  24 |   0 |
|        2 |  11 |  21 |   1 |

#### MannKS (Merged)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |  18 |  24 |   0 |
|        2 |  11 |  21 |   1 |

#### MannKS (Bagging)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |  23 |  19 |   0 |
|        2 |  13 |  19 |   1 |

## 2. Breakpoint Location Accuracy
Absolute Error when the correct number of breakpoints was found.

| Method | Mean | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise (OLS) | 4.4892 | 7.0648 | 0.0000 | 30.2054 |
| MannKS (Standard AIC) | 4.3107 | 8.5997 | 0.0000 | 39.8133 |
| MannKS (Merged) | 4.3120 | 8.6078 | 0.0000 | 39.8133 |
| MannKS (Bagging) | 3.0433 | 5.7412 | 0.0000 | 26.7799 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments?
    *   **Neutral.** Performance was identical.
*   **Bagging:** How does the bagging method perform?
    *   Bagging accuracy: 45.0%.
