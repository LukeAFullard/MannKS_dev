# LWP-TRENDS R Script: Function and Parameter Analysis

This document provides a detailed breakdown of the key functions and their parameters within the `LWPTrends_v2502.r` script. It is intended to serve as a reference for the verification process and for understanding the methodology of the original LWP-TRENDS tool.

## High-Level Wrapper Functions

These are the main functions a user would typically call to perform a trend analysis.

### 1. `NonSeasonalTrendAnalysis`

*   **Purpose:** Acts as a high-level wrapper to perform a standard (non-seasonal) Mann-Kendall test and Sen's slope analysis. It calls the lower-level `MannKendall` and `SenSlope` functions internally.
*   **Signature:** `NonSeasonalTrendAnalysis(x, do.plot=F, ...)`
*   **Parameters:**
    *   `x`: A pre-processed R `data.frame`. This is the most critical input. The function expects this dataframe to have specific columns created by the pre-processing functions, including `RawValue`, `Censored`, `CenType`, `myDate`, `Year`, and `TimeIncr`.
    *   `do.plot` (boolean, default: `FALSE`): If `TRUE`, the function will generate and return a ggplot object visualizing the trend.
    *   `...`: Ellipsis to pass additional arguments down to the internal `MannKendall` and `SenSlope` functions. This is how key parameters like `HiCensor`, `ValuesToUse`, and aggregation settings are controlled.

### 2. `SeasonalTrendAnalysis`

*   **Purpose:** Acts as a high-level wrapper for seasonal trend analysis. It calls `SeasonalKendall` and `SeasonalSenSlope` internally.
*   **Signature:** `SeasonalTrendAnalysis(x, do.plot=F, ...)`
*   **Parameters:**
    *   `x`: A pre-processed R `data.frame`. Similar to the non-seasonal version, this dataframe must be correctly prepared with columns like `RawValue`, `Censored`, `myDate`, `Year`, and a `Season` column. The `GetSeason` function is typically used to determine and create the `Season` column.
    *   `do.plot` (boolean, default: `FALSE`): If `TRUE`, generates a trend plot.
    *   `...`: Passes arguments down to the lower-level seasonal functions.

## Core Analysis Functions

These functions are called by the high-level wrappers and contain the main statistical logic.

### 1. `MannKendall` / `SeasonalKendall`

*   **Purpose:** Performs the Mann-Kendall / Seasonal Mann-Kendall test for significance.
*   **Key Parameters (passed via `...`):**
    *   `ValuesToUse` (string, default: `"RawValue"`): The name of the column in the input dataframe `x` that contains the numeric data for the trend test.
    *   `HiCensor` (boolean or numeric, default: `FALSE`): Implements the "high censor" rule. If `TRUE`, all values (censored or not) below the highest left-censor limit are treated as censored at that limit. If a numeric value is provided, that value is used as the censoring threshold.
    *   `TimeIncrMed` (boolean, default: `TRUE`): Controls temporal aggregation. When `TRUE`, the data is aggregated to a single value per time increment (e.g., one value per year) using the method defined by `UseMidObs`. This is a critical parameter for emulating LWP-TRENDS.
    *   `UseMidObs` (boolean, default: `TRUE`): Determines the aggregation method when `TimeIncrMed` is `TRUE`. If `TRUE`, it selects the observation closest to the theoretical midpoint of the time period. If `FALSE`, it calculates the median of all observations within the period.

### 2. `SenSlope` / `SeasonalSenSlope`

*   **Purpose:** Calculates the Sen's slope (the median of all pairwise slopes) and its confidence intervals.
*   **Key Parameters (passed via `...`):**
    *   Accepts the same key parameters as the Kendall functions: `ValuesToUse`, `HiCensor`, `TimeIncrMed`, and `UseMidObs`. It is critical that these are set consistently for both the significance test and the slope calculation.
    *   `RawValues` (boolean, default: `TRUE`): This parameter has a subtle but important role. It controls how censored values are handled *internally* for the Sen's slope calculation. The script substitutes left-censored values with `value * 0.5` and right-censored values with `value * 1.1` to avoid ties. This parameter ensures this substitution happens correctly, especially when dealing with flow-adjusted data. For standard verification, it should be left as `TRUE`.

## Pre-Processing and Data Preparation Functions

A user of the R script **must** run these functions in the correct order to prepare the data before calling the analysis wrappers.

### 1. `RemoveAlphaDetect`

*   **Purpose:** Converts a column with mixed numeric and censored string data (e.g., `"5"`, `"<2"`, `">10"`) into three separate columns required by all downstream functions.
*   **Signature:** `RemoveAlphaDetect(Data, ColToUse="Value")`
*   **Parameters:**
    *   `Data`: The input `data.frame`.
    *   `ColToUse` (string, default: `"Value"`): The name of the column containing the data to be processed.
*   **Output:** Returns the dataframe with three new columns:
    *   `RawValue`: The numeric value (e.g., `2` for `"<2"`).
    *   `Censored`: A boolean (`TRUE`/`FALSE`) indicating if the value was censored.
    *   `CenType`: A factor (`"lt"`, `"gt"`, `"not"`) indicating the type of censoring.

### 2. `GetMoreDateInfo`

*   **Purpose:** Adds several date-related columns to the dataframe that are essential for seasonal analysis and grouping.
*   **Signature:** `GetMoreDateInfo(Data, firstMonth=1, FindDateShifts=TRUE)`
*   **Parameters:**
    *   `Data`: The input `data.frame`, which must include a date column named `myDate`.
    *   `firstMonth` (integer, default: `1`): Defines the starting month of a "custom year" for analysis.
    *   `FindDateShifts` (boolean, default: `TRUE`): A complex feature that attempts to shift dates at the very end of one month to the next month if certain conditions are met. For verification, it's often simpler to disable this (`FALSE`) to ensure dates are handled literally.
*   **Output:** Returns the dataframe with new columns like `Year`, `Month`, `Qtr`, etc.

### 3. `InspectTrendData`

*   **Purpose:** A multi-purpose function that filters the data to a specific trend period and determines the highest frequency time increment (e.g., Monthly, Quarterly) that has sufficient data for a reliable analysis.
*   **Signature:** `InspectTrendData(x, Year = "Year", TrendPeriod = NA, EndYear = NA, ...)`
*   **Parameters:**
    *   `x`: The input `data.frame`.
    *   `Year` (string, default: `"Year"`): The name of the column containing the year.
    *   `TrendPeriod` (integer, default: `NA`): The length of the trend analysis period in years. If `NA`, it's calculated from the data.
    *   `EndYear` (integer, default: `NA`): The final year of the analysis period.
    *   `propIncrTol` / `propYearTol` (float, defaults: `0.9`): Data sufficiency thresholds.
*   **Output:** Returns the filtered dataframe with a new column, `TimeIncr`, which is set to the determined analysis frequency (e.g., 'Monthly'). This column is used by downstream functions.
