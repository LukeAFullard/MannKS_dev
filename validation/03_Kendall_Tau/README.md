# Validation Report

## Plots
### v03_tied.png
![v03_tied.png](v03_tied.png)

## Results
| Test ID               | Method                |   Slope |     P-Value |   Lower CI |   Upper CI |
|:----------------------|:----------------------|--------:|------------:|-----------:|-----------:|
| V-03_tau_b_comparison | MannKenSen (Standard) | 5.00685 | 9.58249e-08 |    4.01815 |    5.96814 |
| V-03_tau_b_comparison | MannKenSen (LWP Mode) | 5.00685 | 9.58249e-08 |    4.01815 |    5.96814 |
| V-03_tau_b_comparison | LWP-TRENDS (R)        | 5.00342 | 1.31191e-08 |    4.28697 |    5.46781 |
| V-03_tau_b_comparison | MannKenSen (ATS)      | 5.00685 | 9.58249e-08 |    4.01815 |    5.96814 |
| V-03_tau_b_comparison | NADA2 (R)             | 5.00685 | 1.31191e-08 |  nan       |  nan       |
| V-03_tau_a_comparison | MannKenSen (Standard) | 5.00685 | 9.58249e-08 |    4.01815 |    5.96814 |
| V-03_tau_a_comparison | MannKenSen (LWP Mode) | 5.00685 | 9.58249e-08 |    4.01815 |    5.96814 |
| V-03_tau_a_comparison | LWP-TRENDS (R)        | 5.00342 | 1.31191e-08 |    4.28697 |    5.46781 |
| V-03_tau_a_comparison | MannKenSen (ATS)      | 5.00685 | 9.58249e-08 |    4.01815 |    5.96814 |
| V-03_tau_a_comparison | NADA2 (R)             | 5.00685 | 1.31191e-08 |  nan       |  nan       |

## LWP Accuracy (Python vs R)
| Test ID               |   Slope Error |   Slope % Error |
|:----------------------|--------------:|----------------:|
| V-03_tau_b_comparison |    0.00342935 |       0.0685401 |
| V-03_tau_a_comparison |    0.00342935 |       0.0685401 |
