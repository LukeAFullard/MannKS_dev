# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| OLS_Piecewise | 72.0% | 0.2563 |
| MannKS_BIC | 58.0% | 4.4986 |
| MannKS_mBIC | 49.0% | 3.5664 |
| MannKS_AIC | 71.0% | 6.4039 |
| MannKS_AIC_Merge | 69.0% | 6.2330 |
| MannKS_AIC_Bagging | 68.0% | 57.2492 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| OLS_Piecewise | 5.7286 | 5.9449 | 0.0154 | 25.8255 |
| MannKS_BIC | 4.8119 | 4.8768 | 0.1821 | 24.0548 |
| MannKS_mBIC | 3.8690 | 3.2401 | 0.1696 | 12.2586 |
| MannKS_AIC | 6.0695 | 5.9711 | 0.1696 | 28.4088 |
| MannKS_AIC_Merge | 5.5287 | 5.2075 | 0.1696 | 24.0548 |
| MannKS_AIC_Bagging | 5.4633 | 5.9035 | 0.0154 | 30.2117 |

## 3. Breakdown by True Breakpoint Count (N)

### True N = 0
(Sample Size: 25)
| Method | Selection Accuracy | Loc MAE (Correct N only) |
| :--- | :--- | :--- |
| OLS_Piecewise | 100.0% | N/A |
| MannKS_BIC | 100.0% | N/A |
| MannKS_mBIC | 100.0% | N/A |
| MannKS_AIC | 100.0% | N/A |
| MannKS_AIC_Merge | 100.0% | N/A |
| MannKS_AIC_Bagging | 100.0% | N/A |

### True N = 1
(Sample Size: 38)
| Method | Selection Accuracy | Loc MAE (Correct N only) |
| :--- | :--- | :--- |
| OLS_Piecewise | 89.5% | 5.1043 |
| MannKS_BIC | 81.6% | 5.0166 |
| MannKS_mBIC | 63.2% | 3.8690 |
| MannKS_AIC | 86.8% | 5.4675 |
| MannKS_AIC_Merge | 89.5% | 5.3827 |
| MannKS_AIC_Bagging | 84.2% | 4.8989 |

### True N = 2
(Sample Size: 37)
| Method | Selection Accuracy | Loc MAE (Correct N only) |
| :--- | :--- | :--- |
| OLS_Piecewise | 35.1% | 7.3613 |
| MannKS_BIC | 5.4% | 1.6382 |
| MannKS_mBIC | 0.0% | No Correct Hits |
| MannKS_AIC | 35.1% | 7.5976 |
| MannKS_AIC_Merge | 27.0% | 6.0253 |
| MannKS_AIC_Bagging | 29.7% | 7.1053 |
