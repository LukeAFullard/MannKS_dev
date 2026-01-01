# Welcome to MannKenSen Analysis Tool

**Robust Statistical Analysis for Environmental Data**

This tool provides a user-friendly interface for the `MannKS` Python library, designed specifically for analyzing trends in environmental time series data. It is particularly powerful because it can handle:

*   **Unequally Spaced Data:** Unlike many standard tools, it does not require your data to be collected at perfectly regular intervals.
*   **Censored Data (Non-Detects):** It correctly handles values reported as "less than detection limit" (e.g., `<0.05`) without substituting arbitrary values like half the detection limit, using statistically robust methods.
*   **Seasonality:** It automatically detects and accounts for seasonal patterns (e.g., monthly or quarterly cycles) that can obscure long-term trends.

### How to Use This Tool

1.  **Dashboard Tab:** This is your main workspace.
    *   **Upload Data:** Load your CSV or Excel file.
    *   **Auto-Analysis (Default):** Just set your significance level and seasonal period (e.g., 12 for months), and the tool will automatically check for seasonality and run the correct trend test.
    *   **Advanced Mode:** Toggle this to gain full control over every statistical parameter, including aggregation methods, high-censor rules, and specific test algorithms.

2.  **Report Tab:** View a history of all analyses run in your session and download a comprehensive HTML report.

### Key Features

*   **Mann-Kendall Test:** Non-parametric test for monotonic trends.
*   **Seasonal Mann-Kendall:** Extension for seasonal data.
*   **Sen's Slope Estimator:** Robust magnitude of trend.
*   **Akritas-Theil-Sen (ATS):** Advanced censored data slope estimator.
*   **Data Inspection:** Visualize your data density and censoring patterns.

*Developed for robust, defensible environmental data analysis.*
