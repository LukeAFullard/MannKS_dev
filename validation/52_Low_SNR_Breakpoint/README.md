# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 70.0% | 4.2786 |
| MannKS_Robust | 68.0% | 1.1280 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 5.9180 | 5.3729 | 0.1353 | 22.4948 |
| MannKS_Robust | 6.8170 | 6.5885 | 0.0815 | 25.1538 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 12 | 0 | 0 |
| **1** | 3 | 18 | 2 |
| **2** | 0 | 10 | 5 |

### MannKS_Robust
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 12 | 0 | 0 |
| **1** | 3 | 18 | 2 |
| **2** | 0 | 11 | 4 |
