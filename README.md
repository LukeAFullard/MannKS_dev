# MannKenSen

`MannKenSen` is a Python package for conducting Mann-Kendall trend tests and calculating Sen's slope. It is specifically designed to handle the complexities of real-world environmental and time-series data, including **unequally spaced timestamps**, **censored data**, **seasonality**, and the need for **regional-level trend aggregation**.

The statistical methods are heavily inspired by the robust LWP-TRENDS R package.

---

## Getting Started: A User Guide Through Examples

The best way to learn how to use the `MannKenSen` package is to follow our comprehensive user guide. It is a collection of self-contained examples that walk you through every feature of the library, from basic tests to advanced, nuanced scenarios.

**[Click here to access the full User Guide](./Examples/README.md)**

---

## Features

- **Mann-Kendall Trend Test:** Performs the Mann-Kendall test for monotonic trends.
- **Sen's Slope Estimator:** Calculates the Sen's slope, a robust, non-parametric estimate of the trend magnitude.
- **Unequally Spaced Time Series:** A core feature of the package is its ability to correctly handle data that is not collected at regular time intervals.
- **Censored Data Handling:** Provides a full suite of tools to work with censored data (e.g., values below a detection limit like `"<5"` or `">100"`), including robust statistical methods and options for compatibility with legacy systems.
- **Seasonal Trend Analysis:** Supports seasonal trend testing for various seasonal patterns (e.g., monthly, quarterly, weekly, daily).
- **Seasonality Checking:** Includes statistical tests (`check_seasonality`) and plotting utilities (`plot_seasonal_distribution`) to determine if your data has a seasonal pattern *before* you run a seasonal test.
- **Regional Trend Aggregation:** Provides a `regional_test` function to aggregate trend results from multiple sites while correcting for inter-site correlation, allowing for a statistically sound regional trend assessment.
- **Data Quality Warnings:** An "Analysis Notes" system automatically flags potential issues with your data, such as small sample sizes or an over-reliance on censored data for slope calculations.
- **Plotting Utilities:** Built-in plotting functions to visualize trends, confidence intervals, and seasonal distributions.
- **Customizable Trend Classification:** Automatically classifies trends into human-readable categories (e.g., "Likely Increasing") and allows for user-defined classification rules.

## Installation

To install the necessary dependencies for this package, run the following command:

```bash
pip install -r requirements.txt
```
To install the package itself in an editable mode for development:
```bash
pip install -e .
```

## Quick Start Example

Here is a brief example of a non-seasonal trend test with censored data. For a full explanation, please see our detailed examples.

```python
import numpy as np
import pandas as pd
from MannKenSen import prepare_censored_data, trend_test

# 1. Create a time vector
t = pd.to_datetime(pd.date_range(start='2010-01-01', periods=10, freq='YE'))

# 2. Create a data vector with mixed numeric and censored string values
x_raw = [5, '<4', 3.5, '>6', 6.2, '<4', 3, 2.5, '<2', 2.1]

# 3. Pre-process the censored data into the required DataFrame format
x_prepared = prepare_censored_data(x_raw)

# 4. Run the trend test
result = trend_test(x=x_prepared, t=t)

print(result)
```

## Comparison to LWP-TRENDS R Script

While the `MannKenSen` package is heavily inspired by the LWP-TRENDS R script, it is not a 1:1 clone. Users should be aware of key methodological differences in areas such as time vector handling and the default methods for censored data. For a full breakdown of these differences, please consult the package's internal documentation.

## References

1. Helsel, D.R. (2012). *Statistics for Censored Environmental Data Using Minitab and R* (2nd ed.). Wiley.
2. Gilbert, R.O. (1987). *Statistical Methods for Environmental Pollution Monitoring*. Wiley.
3. Hirsch, R.M., Slack, J.R., & Smith, R.A. (1982). Techniques of trend analysis for monthly water quality data. *Water Resources Research*, 18(1), 107-121.
4. van Belle, G., & Hughes, J.P. (1984). Nonparametric tests for trend in water quality. *Water Resources Research*, 20(1), 127-136.
5. Mann, H.B. (1945). Nonparametric tests against trend. *Econometrica*, 13(3), 245-259.
6. Sen, P.K. (1968). Estimates of the regression coefficient based on a particular kind of rank correlation. *Journal of the American Statistical Association*, 63(324), 1379-1389.
