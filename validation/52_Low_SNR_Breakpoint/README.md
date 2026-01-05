# Validation 52: Low SNR Breakpoint Detection

Comparision across 100 random datasets (Non-censored, Low SNR, Sigma=5.0) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 40.0% |
| MannKS (Standard) | 35.0% |
| **MannKS (Merged)** | **35.0%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   -1 |   0 |   1 |   2 |
|---------:|-----:|----:|----:|----:|
|        0 |    8 |  17 |   0 |   0 |
|        1 |    8 |  10 |  22 |   2 |
|        2 |    3 |   7 |  22 |   1 |

#### MannKS (Standard)
|   true_n |   0 |   1 |
|---------:|----:|----:|
|        0 |  25 |   0 |
|        1 |  32 |  10 |
|        2 |  21 |  12 |

#### MannKS (Merged)
|   true_n |   0 |   1 |
|---------:|----:|----:|
|        0 |  25 |   0 |
|        1 |  32 |  10 |
|        2 |  21 |  12 |

## 2. Breakpoint Location Accuracy
Mean Absolute Error (MAE) when the correct number of breakpoints was found.

| Method | Mean Location Error |
| :--- | :--- |
| Piecewise (OLS) | 4.4892 |
| MannKS (Standard) | 0.8555 |
| MannKS (Merged) | 0.8208 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments (specifically reducing over-segmentation)?
    *   **Neutral.** Performance was identical.
*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?
    *   MannKS (Merged) is within 5.0% accuracy of OLS.

## 4. Example Plots
![Example 0](example_plot_0.png)
![Example 1](example_plot_1.png)
![Example 2](example_plot_2.png)
