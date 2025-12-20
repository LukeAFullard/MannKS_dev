
# MannKenSen: A User Guide Through Examples

Welcome to the user guide for the `MannKenSen` Python package. This collection of examples is designed to be a practical, hands-on guide to all the features of the library, from basic trend tests to advanced seasonal analysis.

Each example is a self-contained "chapter" that includes the full Python code, the exact output, and a detailed interpretation of the results.

## Table of Contents

### Part 1: Core Concepts & Basic Workflow
*   [**Example 01: Getting Started - Inspecting Your Data**](./01_Getting_Started_Inspecting_Data/README.md)
*   [**Example 02: Basic Non-Seasonal Trend Test (Numeric Time)**](./02_Basic_Non_Seasonal_Numeric/README.md)
*   [**Example 03: Non-Seasonal Trend Test with Timestamps**](./03_Non_Seasonal_Timestamps/README.md)
*   [**Example 04: Handling Basic Censored Data**](./04_Handling_Censored_Data/README.md)
*   [**Example 05: Checking For & Visualizing Seasonality**](./05_Checking_for_Seasonality/README.md)
*   [**Example 06: Basic Seasonal Trend Test**](./06_Basic_Seasonal_Trend_Test/README.md)

### Part 2: Handling Complex & Messy Data
*   [**Example 07: Deep Dive into Censored Data Options**](./07_Censored_Data_Options/README.md)
*   [**Example 08: The High Censor Rule (`hicensor`)**](./08_High_Censor_Rule/README.md)
*   [**Example 09: Aggregation for Tied and Clustered Data**](./09_Aggregation_Tied_Clustered_Data/README.md)
*   [**Example 10: Comparing Right-Censored Data Methods (`mk_test_method`)**](./10_Right_Censored_Methods/README.md)
*   [**Example 11: Handling Data with Multiple Censoring Levels**](./11_Multiple_Censoring_Levels/README.md)

### Part 3: Advanced Features & Nuances
*   [**Example 12: Advanced Seasonality (Non-Monthly Data)**](./12_Advanced_Seasonality/README.md)
*   [**Example 13: The Impact of Censored Data Multipliers**](./13_Censored_Data_Multipliers/README.md)
*   [**Example 14: Comparing Confidence Interval Methods**](./14_Confidence_Interval_Methods/README.md)
*   [**Example 15: Time Vector Nuances (Numeric Data)**](./15_Time_Vector_Nuances/README.md)
*   [**Example 16: Regional Trend Analysis**](./16_Regional_Trend_Analysis/README.md)

### Part 4: Interpreting Results & Validation
*   [**Example 17: Interpreting the Full Output**](./17_Interpreting_Output/README.md)
*   [**Example 18: Interpreting Analysis Notes**](./18_Interpreting_Analysis_Notes/README.md)
*   [**Example 19: Standalone Trend Classification**](./19_Standalone_Classification/README.md)
*   [**Example 20: Visual Diagnostics of Trend Plots**](./20_Visual_Diagnostics/README.md)
*   [**Example 21: Sen's Slope Methods for Censored Data (`sens_slope_method`)**](./21_Sens_Slope_Methods/README.md)

### Part 5: Advanced Seasonal Analysis
*   [**Example 22: Seasonal Trend with Weekly Data**](./22_Seasonal_Weekly_Data/README.md)
*   [**Example 23: Seasonal Trend with Daily Data (No Trend)**](./23_Seasonal_Daily_No_Trend/README.md)
*   [**Example 24: Seasonal Trend with Hourly Data**](./24_Seasonal_Hourly_Increasing_Trend/README.md)
*   [**Example 25: Advanced Seasonality with `day_of_year`**](./25_Seasonal_Day_Of_Year/README.md)

### Part 6: Advanced Parameter Nuances
*   [**Example 26: Advanced Parameter Nuances**](./26_advanced_parameter_nuances/README.md)

---

### Detailed Guides

For a deeper dive into specific topics, see our detailed reference guides. These explain the key concepts and optional parameters in much greater detail than the examples.

*   [**A Guide to Core Concepts in MannKenSen**](./Detailed_guides/core_concepts_guide.md)
    -   **What is it?** This guide explains the fundamental data model of the package, including the correct data types for your time (`t`) and data (`x`) vectors.
    -   **When to read:** Read this first if you are new to the package or if you have questions about `datetime` objects vs. strings.

*   [**A Comprehensive Guide to `check_seasonality` and Aggregation**](./Detailed_Guides/check_seasonality_guide/README.md)
    -   **What is it?** This guide explains how to use the `check_seasonality` function and why it's crucial to use consistent data aggregation between this check and the final trend test.
    -   **When to read:** Read this before you perform a seasonal trend test to ensure your workflow is statistically sound.

*   [**A Comprehensive Guide to Analysis Notes**](./Detailed_Guides/analysis_notes_guide.md)
    -   **What is it?** This guide explains the data quality warnings (e.g., `"Long run of single value"`) that the package might return with your results.
    -   **When to read:** Read this if you get a warning in your `analysis_notes` output and want to understand what it means and what actions you should take.

*   [**A Comprehensive Guide to Trend Classification**](./Detailed_Guides/trend_classification_guide.md)
    -   **What is it?** This guide explains how the package automatically assigns a descriptive trend category (like `"Likely Increasing"` or `"Stable"`) based on the statistical results.
    -   **When to read:** Read this to understand the default classification system (inspired by the IPCC) or if you want to learn how to define your own custom classification rules.

*   [**A Comprehensive Guide to Interpreting Test Outputs**](./Detailed_Guides/interpreting_test_outputs_guide/README.md)
    -   **What is it?** This is a detailed reference for every field in the result object returned by the test functions.
    -   **When to read:** Read this to understand the meaning of `p`, `z`, `Tau`, `slope`, and all other output values.

*   [**A Comprehensive Guide to `regional_test`**](./Detailed_Guides/regional_test_guide/README.md)
    -   **What is it?** This guide explains how to perform a regional trend analysis, which aggregates results from multiple sites to determine an overall trend.
    -   **When to read:** Read this when you have data from multiple locations and want to know if there is a consistent trend across the entire region.

*   [**A Comprehensive Guide to `trend_test` Parameters**](./Detailed_Guides/trend_test_parameters_guide.md)
    -   **What is it?** This is a detailed reference for every optional parameter in the main `trend_test` function.
    -   **When to read:** Read this when you want to move beyond a basic analysis and fine-tune the test by handling censored data, aggregation, or other advanced features.

*   [**A Comprehensive Guide to `seasonal_trend_test` Parameters**](./Detailed_Guides/seasonal_trend_test_parameters_guide.md)
    -   **What is it?** This is a detailed reference for every optional parameter in the `seasonal_trend_test` function, focusing on seasonality and aggregation.
    -   **When to read:** Read this when you need to configure a seasonal analysis for a specific data structure (e.g., daily, weekly) or customize how the function handles data within each season.


---
*This guide is programmatically generated. To update an example, modify the `run_example.py` in the respective directory.*
