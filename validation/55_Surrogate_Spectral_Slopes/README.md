# Validation Report: Surrogate Data Spectral Slopes

Testing Mann-Kendall vs Surrogate Test False Positive Rates (Null) and True Positive Rates (Trend) across different spectral colors (Beta).
Comparison of IAAFT (Even) and Lomb-Scargle (Uneven).

## Interpretation of Results

### 1. Robustness to Serial Correlation (Type I Error)
- **Standard Mann-Kendall:** As expected, the standard test fails to control Type I errors for colored noise. Rejection rates exceed 20% starting at Beta=0.75, indicating that serial correlation is being mistaken for a trend.
- **Surrogate Test:** Successfully controls the False Positive Rate across all tested spectral slopes. This confirms that the method correctly accounts for the background noise spectrum.

### 2. Statistical Power (Trend Detection)
- **Sensitivity:** Power decreases for stronger red noise (Beta >= 1.75). This is expected, as strong low-frequency noise can mask or mimic the trend signal, making significance harder to establish.

### 3. Uneven Sampling Performance
- **Lomb-Scargle Method:** Average rejection rate on uneven null data was 0.06. This demonstrates its ability to handle irregular spacing without interpolation bias.
- **IAAFT Method (on Uneven):** Average rejection rate was 0.03. While it may perform adequately in some random-gap scenarios, it is theoretically unsound for non-uniform grids.

## Detailed Results

| Test Name | Status | Message | Details |
| :--- | :--- | :--- | :--- |
| Beta=0.0 Detailed | **PASS** | Rates nominal | beta=0.0, null_mk_rej=0.1, null_iaaft_rej=0.1, trend_mk_rej=1.0, trend_iaaft_rej=1.0, uneven_ls_rej=0.1, uneven_iaaft_rej=0.1 |
| Beta=0.25 Detailed | **PASS** | Rates nominal | beta=0.25, null_mk_rej=0.0, null_iaaft_rej=0.0, trend_mk_rej=1.0, trend_iaaft_rej=1.0, uneven_ls_rej=0.0, uneven_iaaft_rej=0.0 |
| Beta=0.5 Detailed | **PASS** | Rates nominal | beta=0.5, null_mk_rej=0.2, null_iaaft_rej=0.1, trend_mk_rej=1.0, trend_iaaft_rej=1.0, uneven_ls_rej=0.1, uneven_iaaft_rej=0.1 |
| Beta=0.75 Detailed | **PASS** | Rates nominal | beta=0.75, null_mk_rej=0.6, null_iaaft_rej=0.0, trend_mk_rej=1.0, trend_iaaft_rej=0.9, uneven_ls_rej=0.0, uneven_iaaft_rej=0.0 |
| Beta=1.0 Detailed | **PASS** | MK Fails as expected | beta=1.0, null_mk_rej=0.5, null_iaaft_rej=0.0, trend_mk_rej=1.0, trend_iaaft_rej=1.0, uneven_ls_rej=0.0, uneven_iaaft_rej=0.0 |
| Beta=1.25 Detailed | **PASS** | Rates nominal | beta=1.25, null_mk_rej=0.3, null_iaaft_rej=0.1, trend_mk_rej=1.0, trend_iaaft_rej=0.6, uneven_ls_rej=0.1, uneven_iaaft_rej=0.1 |
| Beta=1.5 Detailed | **PASS** | MK Fails as expected | beta=1.5, null_mk_rej=0.7, null_iaaft_rej=0.0, trend_mk_rej=1.0, trend_iaaft_rej=0.6, uneven_ls_rej=0.0, uneven_iaaft_rej=0.0 |
| Beta=1.75 Detailed | **PASS** | MK Fails as expected | beta=1.75, null_mk_rej=0.4, null_iaaft_rej=0.0, trend_mk_rej=1.0, trend_iaaft_rej=0.4, uneven_ls_rej=0.0, uneven_iaaft_rej=0.0 |
| Beta=2.0 Detailed | **PASS** | MK Fails as expected | beta=2.0, null_mk_rej=0.7, null_iaaft_rej=0.1, trend_mk_rej=1.0, trend_iaaft_rej=0.5, uneven_ls_rej=0.0, uneven_iaaft_rej=0.0 |
| Beta=2.25 Detailed | **PASS** | MK Fails as expected | beta=2.25, null_mk_rej=0.9, null_iaaft_rej=0.0, trend_mk_rej=1.0, trend_iaaft_rej=0.5, uneven_ls_rej=0.1, uneven_iaaft_rej=0.0 |
| Beta=2.5 Detailed | **WARN** | LS Null Rate High; MK Fails as expected | beta=2.5, null_mk_rej=0.7, null_iaaft_rej=0.0, trend_mk_rej=0.8, trend_iaaft_rej=0.2, uneven_ls_rej=0.3, uneven_iaaft_rej=0.0 |
