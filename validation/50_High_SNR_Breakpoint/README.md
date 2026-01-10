# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 83.3% | 4.6942 |
| MannKS_BIC | 86.7% | 1.1932 |
| MannKS_Hybrid | 83.3% | 4.5281 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 1.1924 | 0.8328 | 0.0501 | 2.5670 |
| MannKS_BIC | 2.1405 | 1.8874 | 0.0208 | 6.4573 |
| MannKS_Hybrid | 1.1924 | 0.8328 | 0.0501 | 2.5670 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.1785 | 0.1658 | 0.0000 | 0.4848 |
| MannKS_BIC | 0.0115 | 0.0125 | 0.0004 | 0.0460 |
| MannKS_Hybrid | 0.0108 | 0.0106 | 0.0004 | 0.0374 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 10 | 2 |
| **2** | 0 | 3 | 7 |

### MannKS_BIC
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 10 | 2 |
| **2** | 0 | 2 | 8 |

### MannKS_Hybrid
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 10 | 2 |
| **2** | 0 | 3 | 7 |
