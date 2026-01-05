# Validation 50: High SNR Breakpoint Detection

Comparision across 100 random datasets (Non-censored, High SNR, Sigma=0.5) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 88.0% |
| MannKS (Standard) | 94.0% |
| **MannKS (Merged)** | **95.0%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   -1 |   0 |   1 |   2 |
|---------:|-----:|----:|----:|----:|
|        0 |    7 |  18 |   0 |   0 |
|        1 |    1 |   0 |  39 |   2 |
|        2 |    1 |   0 |   1 |  31 |

#### MannKS (Standard)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |   0 |  42 |   0 |
|        2 |   0 |   6 |  27 |

#### MannKS (Merged)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  25 |   0 |   0 |
|        1 |   0 |  42 |   0 |
|        2 |   0 |   5 |  28 |

## 2. Breakpoint Location Accuracy
Mean Absolute Error (MAE) when the correct number of breakpoints was found.

| Method | Mean Location Error |
| :--- | :--- |
| Piecewise (OLS) | 0.6867 |
| MannKS (Standard) | 0.6216 |
| MannKS (Merged) | 0.6130 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments (specifically reducing over-segmentation)?
    *   **Yes.** The merging step improved overall accuracy, likely by correcting cases where standard BIC overestimated the number of breakpoints.
*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?
    *   MannKS (Merged) is within 7.0% accuracy of OLS.

## 4. Example Plots
![Example 0](example_plot_0.png)
![Example 1](example_plot_1.png)
![Example 2](example_plot_2.png)
