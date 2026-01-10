# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 93.3% | 4.3584 |
| MannKS_BIC | 90.0% | 1.2685 |
| MannKS_Hybrid | 93.3% | 4.2707 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.8761 | 0.6390 | 0.0781 | 2.1517 |
| MannKS_BIC | 0.8671 | 0.8006 | 0.0029 | 3.9667 |
| MannKS_Hybrid | 0.8761 | 0.6390 | 0.0781 | 2.1517 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.2636 | 0.0244 | 0.2182 | 0.3191 |
| MannKS_BIC | 0.0165 | 0.0099 | 0.0021 | 0.0435 |
| MannKS_Hybrid | 0.0174 | 0.0087 | 0.0037 | 0.0381 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 28 | 2 |

### MannKS_BIC
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 27 | 3 |

### MannKS_Hybrid
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 28 | 2 |
