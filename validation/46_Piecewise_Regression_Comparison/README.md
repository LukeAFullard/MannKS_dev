# Validation 46: Comparison with Truth & `piecewise-regression`

Comparision across 50 random datasets (Non-censored, Normal noise) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 60.0% |
| MannKS (Standard) | 86.0% |
| **MannKS (Merged)** | **86.0%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   1 |   2 |
|---------:|----:|----:|
|        0 |  10 |   2 |
|        1 |  21 |   5 |
|        2 |   3 |   9 |

#### MannKS (Standard)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  12 |   0 |   0 |
|        1 |   0 |  26 |   0 |
|        2 |   0 |   7 |   5 |

#### MannKS (Merged)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  12 |   0 |   0 |
|        1 |   0 |  26 |   0 |
|        2 |   0 |   7 |   5 |

## 2. Breakpoint Location Accuracy
Mean Absolute Error (MAE) when the correct number of breakpoints was found.

| Method | Mean Location Error |
| :--- | :--- |
| Piecewise (OLS) | 2.0905 |
| MannKS (Standard) | 1.3685 |
| MannKS (Merged) | 1.3786 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments (specifically reducing over-segmentation)?
    *   **Neutral.** Performance was identical.
*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?
    *   MannKS (Merged) is within 26.0% accuracy of OLS.
