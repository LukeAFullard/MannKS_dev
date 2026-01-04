# Validation 46: Comparison with Truth & `piecewise-regression`

Comparision across 200 random datasets (Non-censored, Normal noise) against **Ground Truth**.

## 1. Model Selection Accuracy (Finding Correct Number of Breakpoints)
| Method | Accuracy (Correct N) |
| :--- | :--- |
| Piecewise (OLS) | 66.0% |
| MannKS (Standard) | 83.0% |
| **MannKS (Merged)** | **83.5%** |

### Confusion Matrices (Rows=True N, Cols=Predicted N)
#### Piecewise (OLS)
|   true_n |   -1 |   1 |   2 |
|---------:|-----:|----:|----:|
|        0 |    1 |  40 |   6 |
|        1 |    0 |  80 |   8 |
|        2 |    0 |  13 |  52 |

#### MannKS (Standard)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  47 |   0 |   0 |
|        1 |   3 |  85 |   0 |
|        2 |   2 |  29 |  34 |

#### MannKS (Merged)
|   true_n |   0 |   1 |   2 |
|---------:|----:|----:|----:|
|        0 |  47 |   0 |   0 |
|        1 |   3 |  85 |   0 |
|        2 |   2 |  28 |  35 |

## 2. Breakpoint Location Accuracy
Mean Absolute Error (MAE) when the correct number of breakpoints was found.

| Method | Mean Location Error |
| :--- | :--- |
| Piecewise (OLS) | 1.7386 |
| MannKS (Standard) | 1.2602 |
| MannKS (Merged) | 1.2638 |

## 3. Analysis
*   **Accuracy:** Does enabling merging improve the detection of the correct number of segments (specifically reducing over-segmentation)?
    *   **Yes.** The merging step improved overall accuracy, likely by correcting cases where standard BIC overestimated the number of breakpoints.
*   **Comparison to OLS:** Piecewise OLS is theoretically optimal for this normal noise data. How close is MannKS?
    *   MannKS (Merged) is within 17.5% accuracy of OLS.
