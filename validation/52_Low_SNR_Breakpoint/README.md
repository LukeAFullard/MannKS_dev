# Validation 52: Low SNR Breakpoint Detection

Comparision across 5 random datasets (Non-censored, Low SNR, Sigma=5.0) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 20.0% |
| MannKS (Standard AIC) | 40.0% |
| MannKS (Merged) | 40.0% |
| **MannKS (Bagging)** | **40.0%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   -1 |   1 |
|---------:|-----:|----:|
|        0 |    1 |   0 |
|        1 |    0 |   1 |
|        2 |    1 |   2 |

#### MannKS (Standard AIC)
|   true_n |   0 |   1 |
|---------:|----:|----:|
|        0 |   1 |   0 |
|        1 |   0 |   1 |
|        2 |   1 |   2 |

#### MannKS (Merged)
|   true_n |   0 |   1 |
|---------:|----:|----:|
|        0 |   1 |   0 |
|        1 |   0 |   1 |
|        2 |   1 |   2 |

#### MannKS (Bagging)
|   true_n |   0 |   1 |
|---------:|----:|----:|
|        0 |   1 |   0 |
|        1 |   0 |   1 |
|        2 |   1 |   2 |

## 2. Breakpoint Location Accuracy
Mean Absolute Error (MAE) when the correct number of breakpoints was found.

| Method | Mean Location Error |
| :--- | :--- |
| Piecewise (OLS) | 2.7538 |
| MannKS (Standard AIC) | 0.3222 |
| MannKS (Merged) | 0.3426 |
| MannKS (Bagging) | 0.8111 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments?
    *   **Neutral.** Performance was identical.
*   **Bagging:** How does the bagging method perform?
    *   Bagging accuracy: 40.0%.
    *   Bagging Mean Location Error: 0.8111 (vs Standard: 0.3222)
*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?
    *   MannKS (Bagging) is within 20.0% accuracy of OLS.

## 4. Example Plots
![Example 0](example_plot_0.png)
![Example 1](example_plot_1.png)
![Example 2](example_plot_2.png)
