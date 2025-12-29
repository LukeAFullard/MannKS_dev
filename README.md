<div align="center">
  <img src="assets/logo.png" alt="MannKenSen Logo" width="300"/>

  # MannKenSen

  **Robust Trend Analysis for Environmental Data in Python**
</div>

---

## 👋 Welcome

Welcome to **MannKenSen**, a friendly and powerful Python package designed to help you analyze trends in your data.

Whether you are tracking water quality, climate metrics, or any other time-series data, `MannKenSen` makes it easy to perform statistically rigorous tests—even if your data is "messy."

We built this tool specifically to handle the real-world challenges data scientists and environmental engineers face every day:
*   **Irregular sampling?** No problem. existing Python packages like `pyMannKendall` often do not account for unequally sampled time series, leading to inaccurate slope estimates. `MannKenSen` correctly handles this by using the exact time difference between observations.
*   **Missing or "censored" values (like `<5` or `>100`)?** We handle those natively.
*   **Seasonal patterns?** We can detect and account for them.

### 🙏 Inspiration & Credit
This package was heavily inspired by the excellent work done by **[LandWaterPeople (LWP)](https://landwaterpeople.co.nz/)**. Much of the robust functionality for handling censored data and regional aggregation is based on their R scripts and methodologies. We owe them a debt of gratitude for their contributions to the field.

---

## 🚀 Getting Started

The best way to learn is by doing. We have prepared a comprehensive **User Guide** that takes you from a basic "Hello World" trend test to advanced regional analysis.

### [📚 Click here to open the User Guide](./Examples/README.md)

Each example is a self-contained "mini-chapter" with code you can run and explanations of the results.

---

## ✨ Key Features

*   **📈 Mann-Kendall Trend Test**: Scientifically verify if your data is increasing, decreasing, or stable over time.
*   **📐 Sen's Slope Estimator**: Calculate the *magnitude* of the trend (e.g., "increasing by 0.5 units per year").
*   **🛡️ Robust Data Handling**:
    *   **Censored Data**: Specialized support for data with detection limits (e.g., values reported as `<0.1`).
    *   **Unequal Spacing**: Works perfectly with data collected at irregular intervals (e.g., daily sampling followed by monthly sampling).
*   **🍂 Seasonal Analysis**:
    *   **Seasonal Trend Test**: Separate the seasonal signal from the long-term trend.
    *   **Seasonality Check**: Automatically test if your data exhibits seasonality.
*   **🌍 Regional Aggregation**: Combine results from multiple monitoring sites to see the "big picture" for a region.
*   **📊 Visualization**: Built-in plotting tools to visualize your trends and confidence intervals instantly.

---

## 📦 Installation

You can install the package and its dependencies using `pip`.

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Install MannKenSen**
```bash
pip install -e .
```

---

## ⚡ Quick Start

Here is a simple example to get you running in seconds. We will look for a trend in a dataset that includes "censored" values (values below a detection limit).

```python
import pandas as pd
from MannKenSen import prepare_censored_data, trend_test

# 1. Prepare your data
# We have values, some of which are 'censored' (marked with <)
values = [10, 12, '<5', 14, 15, 18, 20, '<5', 25, 30]
dates = pd.date_range(start='2020-01-01', periods=len(values), freq='ME') # Month End

# 2. Process the censored data
# This converts strings like '<5' into a format our statistical engine understands
data = prepare_censored_data(values)

# 3. Run the test
# We scale the slope to 'year' so the output is in units per year
result = trend_test(x=data, t=dates, slope_scaling='year')

# 4. See the results
print(f"Trend Direction: {result.trend}")
print(f"Slope: {result.slope:.2f} units/year")
print(f"P-value: {result.p:.4f}")
```

**What happened?**
The `trend_test` function automatically handled the `<5` values, calculated the trend significance (p-value), and estimated the rate of change (slope).

---

## 📚 References

This package implements standard, peer-reviewed statistical methods.

1.  **Helsel, D.R. (2012).** *Statistics for Censored Environmental Data Using Minitab and R* (2nd ed.). Wiley.
2.  **Gilbert, R.O. (1987).** *Statistical Methods for Environmental Pollution Monitoring*. Wiley.
3.  **Hirsch, R.M., Slack, J.R., & Smith, R.A. (1982).** Techniques of trend analysis for monthly water quality data. *Water Resources Research*, 18(1), 107-121.
4.  **Mann, H.B. (1945).** Nonparametric tests against trend. *Econometrica*, 13(3), 245-259.
5.  **Sen, P.K. (1968).** Estimates of the regression coefficient based on a particular kind of rank correlation. *Journal of the American Statistical Association*, 63(324), 1379-1389.
6.  **Fraser, C., & Whitehead, A. L. (2022).** Continuous measures of confidence in direction of environmental trends at site and other spatial scales. *Environmental Challenges*, 9, 100601.
7.  **Fraser, C., Snelder, T., & Matthews, A. (2018).** State and trends of river water quality in the Manawatu-Whanganui region: for all records up to 30 June 2017. Prepared for Abby Matthews; prepared by Caroline Fraser and Ton Snelder.
