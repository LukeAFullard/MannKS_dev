# Validation 51: Medium SNR Breakpoint Detection

Comparision across 100 random datasets (Non-censored, Medium SNR, Sigma=2.0) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 59.0% |
| MannKS (Standard AIC) | 75.0% |
| MannKS (Merged) | 76.0% |
| **MannKS (Bagging)** | **74.0%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   -1 |   0 |   1 |   2 |
|---------:|-----:|----:|----:|----:|
|        0 |    8 |  17 |   0 |   0 |
|        1 |    4 |   3 |  32 |   3 |
|        2 |    4 |   0 |  19 |  10 |

#### MannKS (Standard AIC)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |   3 |  38 |   1 |
|        2 |   0 |  21 |  12 |

#### MannKS (Merged)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |   3 |  39 |   0 |
|        2 |   1 |  20 |  12 |

#### MannKS (Bagging)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |   5 |  37 |   0 |
|        2 |   1 |  20 |  12 |

## 2. Breakpoint Location Accuracy
Absolute Error when the correct number of breakpoints was found.

| Method | Mean | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise (OLS) | 2.5323 | 3.6467 | 0.0000 | 18.7834 |
| MannKS (Standard AIC) | 2.5205 | 4.1144 | 0.0000 | 20.6324 |
| MannKS (Merged) | 2.4256 | 4.0450 | 0.0000 | 20.6324 |
| MannKS (Bagging) | 2.4479 | 3.7284 | 0.0000 | 18.4567 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments (specifically reducing over-segmentation)?
    *   **Yes.** The merging step improved overall accuracy, likely by correcting cases where standard BIC overestimated the number of breakpoints.
*   **Bagging:** How does the bagging method perform?
    *   Bagging accuracy: 74.0%.
    *   Bagging Mean Location Error: 2.4479 (vs Standard: 2.5205)
*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?
    *   MannKS (Bagging) is within 15.0% accuracy of OLS.

## 4. Example Plots
![Example 0](example_plot_0.png)
![Example 1](example_plot_1.png)
![Example 2](example_plot_2.png)
