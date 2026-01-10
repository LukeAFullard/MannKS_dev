# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 86.7% | 3.8473 |
| MannKS_BIC | 70.0% | 1.3251 |
| MannKS_Hybrid | 86.7% | 4.0314 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.5815 | 0.4177 | 0.0786 | 1.4807 |
| MannKS_BIC | 0.7575 | 0.7689 | 0.0459 | 2.3801 |
| MannKS_Hybrid | 0.5815 | 0.4177 | 0.0786 | 1.4807 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.2650 | 0.0220 | 0.2406 | 0.3220 |
| MannKS_BIC | 0.0176 | 0.0099 | 0.0052 | 0.0408 |
| MannKS_Hybrid | 0.0169 | 0.0098 | 0.0024 | 0.0408 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 26 | 4 |

### MannKS_BIC
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 21 | 9 |

### MannKS_Hybrid
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 26 | 4 |
