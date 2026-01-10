# Validation Results for Examples 46-52

## 46. Piecewise Regression Comparison
*Status: Completed successfully.*
*Outputs: Generated plots (`bp_scatter.png`, `mismatch_plot_0.png`, `mismatch_plot_1.png`) in `validation/46_Piecewise_Regression_Comparison/`.*
*Note: This example does not generate a text-based report.*

---

## 47. Heavy Tail Robustness
*Source: `validation/47_Heavy_Tail_Robustness/README.md`*

# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 93.3% | 4.3584 |
| MannKS_Hybrid | 93.3% | 4.2707 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.8761 | 0.6390 | 0.0781 | 2.1517 |
| MannKS_Hybrid | 0.8761 | 0.6390 | 0.0781 | 2.1517 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.2636 | 0.0244 | 0.2182 | 0.3191 |
| MannKS_Hybrid | 0.0174 | 0.0087 | 0.0037 | 0.0381 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 28 | 2 |

### MannKS_Hybrid
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 28 | 2 |

---

## 48. Outliers Robustness
*Source: `validation/48_Outliers_Robustness/README.md`*

# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 96.7% | 4.6925 |
| MannKS_Hybrid | 93.3% | 4.8089 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 1.2690 | 0.9547 | 0.1134 | 3.3974 |
| MannKS_Hybrid | 1.2011 | 0.8873 | 0.1134 | 2.8808 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.2765 | 0.0384 | 0.2198 | 0.3817 |
| MannKS_Hybrid | 0.0109 | 0.0057 | 0.0017 | 0.0210 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 29 | 1 |

### MannKS_Hybrid
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 28 | 2 |

---

## 49. Heteroscedastic Robustness
*Source: `validation/49_Heteroscedastic_Robustness/README.md`*

# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 86.7% | 3.8473 |
| MannKS_Hybrid | 86.7% | 4.0314 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.5815 | 0.4177 | 0.0786 | 1.4807 |
| MannKS_Hybrid | 0.5815 | 0.4177 | 0.0786 | 1.4807 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.2650 | 0.0220 | 0.2406 | 0.3220 |
| MannKS_Hybrid | 0.0169 | 0.0098 | 0.0024 | 0.0408 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 26 | 4 |

### MannKS_Hybrid
| True N \ Pred N | 1 | 2 |
| :--- | --- | --- |
| **1** | 26 | 4 |

---

## 50. High SNR Breakpoint
*Source: `validation/50_High_SNR_Breakpoint/README.md`*

# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 83.3% | 4.6942 |
| MannKS_Hybrid | 83.3% | 4.5281 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 1.1924 | 0.8328 | 0.0501 | 2.5670 |
| MannKS_Hybrid | 1.1924 | 0.8328 | 0.0501 | 2.5670 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.1785 | 0.1658 | 0.0000 | 0.4848 |
| MannKS_Hybrid | 0.0108 | 0.0106 | 0.0004 | 0.0374 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 10 | 2 |
| **2** | 0 | 3 | 7 |

### MannKS_Hybrid
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 10 | 2 |
| **2** | 0 | 3 | 7 |

---

## 51. Medium SNR Breakpoint
*Source: `validation/51_Medium_SNR_Breakpoint/README.md`*

# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 83.3% | 5.1036 |
| MannKS_Hybrid | 83.3% | 4.8738 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 2.2408 | 1.8406 | 0.1109 | 6.8377 |
| MannKS_Hybrid | 2.2282 | 1.8439 | 0.1109 | 6.8377 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.1068 | 0.1092 | 0.0000 | 0.3806 |
| MannKS_Hybrid | 0.0118 | 0.0128 | 0.0004 | 0.0448 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 11 | 1 |
| **2** | 0 | 4 | 6 |

### MannKS_Hybrid
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 8 | 0 | 0 |
| **1** | 0 | 11 | 1 |
| **2** | 0 | 4 | 6 |

---

## 52. Low SNR Breakpoint
*Source: `validation/52_Low_SNR_Breakpoint/README.md`*

# Validation Report
## 1. Model Selection Accuracy (Correct N)
| Method | Accuracy | Mean Time (s) |
| :--- | :--- | :--- |
| Piecewise_Regression | 71.0% | 4.3081 |
| MannKS_Hybrid | 67.7% | 4.2503 |

## 2. Breakpoint Location Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 6.0436 | 4.6929 | 0.5877 | 17.4792 |
| MannKS_Hybrid | 6.4958 | 5.2928 | 0.5877 | 17.4792 |

## 3. Slope Estimation Accuracy (MAE)
| Method | Mean Error | Std Dev | Min | Max |
| :--- | :--- | :--- | :--- | :--- |
| Piecewise_Regression | 0.0988 | 0.1092 | 0.0000 | 0.3325 |
| MannKS_Hybrid | 0.0092 | 0.0104 | 0.0004 | 0.0422 |

## 3. Confusion Matrix (True N vs Predicted N)

### Piecewise_Regression
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 9 | 0 | 0 |
| **1** | 2 | 9 | 1 |
| **2** | 0 | 6 | 4 |

### MannKS_Hybrid
| True N \ Pred N | 0 | 1 | 2 |
| :--- | --- | --- | --- |
| **0** | 9 | 0 | 0 |
| **1** | 2 | 8 | 2 |
| **2** | 0 | 6 | 4 |
