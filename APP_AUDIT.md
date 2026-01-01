# MannKS App Audit & Analysis

This document contains a deep audit of the Streamlit application located in the `app/` directory. The analysis covers code quality, functionality, user experience (UX), and integration with the `MannKS` library.

## 1. Critical Bugs & Errors

### 1.1. `plot_seasonal_distribution` Input Type Mismatch
*   **Location:** `app/modules/analysis.py` (lines 88-94) and `MannKS/plotting.py`.
*   **Issue:** The `run_analysis` function passes `x_input` (a pandas DataFrame with columns `value`, `censored`, `cen_type`) to `plot_seasonal_distribution`.
    *   The `plot_seasonal_distribution` function in `MannKS` expects a 1D array-like object for `x` and converts it using `np.asarray(x)`.
    *   Passing a DataFrame results in a 2D numpy array. Subsequent operations like `~np.isnan(x_raw)` and plotting will fail or produce incorrect results because the function expects a 1D vector of values.
*   **Fix:** Pass only the value column: `x_input['value']`. Note that `plot_seasonal_distribution` currently does not visually distinguish censored values, so using just the values is the only option unless the library function is updated.

### 1.2. Hardcoded Left-Censoring in Data Loader
*   **Location:** `app/modules/data_loader.py` (line 53)
*   **Issue:** When handling separate "Value" and "Flag" columns, the code explicitly assumes left-censoring:
    ```python
    cen_type = np.where(is_censored, 'lt', 'not')
    ```
*   **Impact:** If a user uploads data with right-censoring (common in some domains), it will be incorrectly treated as left-censored, leading to invalid statistical results.
*   **Fix:** Add a UI option (Radio button) in the "Map Columns" section to let the user specify the censoring type (Left `<` or Right `>`) when using the "Separate Flag" mode.

### 1.3. Missing `hicensor` Parameter
*   **Location:** `app/modules/settings.py`
*   **Issue:** The `hicensor` parameter (High-Censor rule) is a core feature of `trend_test` but is completely missing from the Settings UI.
*   **Impact:** Users cannot enable this important data quality rule.
*   **Fix:** Add a checkbox (and potentially a float input for custom thresholds) in the settings tab.

## 2. UX & Usability Improvements

### 2.1. Date Parsing Fragility
*   **Location:** `app/modules/data_loader.py`
*   **Issue:** `pd.to_datetime(df[time_col])` is used without a format string.
*   **Impact:** Dates like `02/05/2023` are ambiguous (Feb 5th vs May 2nd). Pandas guesses, often inconsistently across rows if formats mix.
*   **Suggestion:** Add an optional "Date Format" text input (e.g., `%Y-%m-%d`) or a selector (Day First / Month First) in the Data Load tab.

### 2.2. "Aggregation Period" Text Input
*   **Location:** `app/modules/settings.py`
*   **Issue:** `tt_agg_period` is a raw text input.
*   **Impact:** Users might type "Year", "yrs", or "annually", which will cause a `ValueError` in the library (which expects specific keys like 'year', 'month').
*   **Suggestion:** Change to a `st.selectbox` with valid options: `['year', 'month', 'quarter', 'week', 'day', 'hour', 'minute', 'second']`.

### 2.3. Missing "Data Inspection"
*   **Location:** General App Flow
*   **Issue:** The `MannKS` library has powerful inspection tools (`inspect_trend_data` / `plot_inspection_data`) that visualize censoring matrices and sample counts. This is absent in the app.
*   **Suggestion:** Add a "Data Inspection" tab or expanding section after loading data that runs these diagnostic plots before the user runs the full analysis.

### 2.4. Download Processed Data
*   **Location:** Data Tab
*   **Issue:** After mapping columns and processing (which handles `<` signs), the user cannot download the "clean" numeric dataset.
*   **Suggestion:** Add a "Download Processed CSV" button.

## 3. Missing Features (Gap Analysis)

| Feature | Status | Recommendation |
| :--- | :--- | :--- |
| **Regional Trend Test** | **Missing** | The library supports `regional_test`. The app should have a mode for this, allowing selection of a "Site ID" column. |
| **Residual Plots** | **Partially Implemented** | The code logic supports it, but the UI (Results tab) does not seem to display the residual plot, only the main trend plot. |
| **Interactive Plots** | **Missing** | Plots are static images. While `MannKS` uses matplotlib, wrapping them in `st.pyplot(fig)` allows some basic interactivity, or using `plotly` for a parallel interactive view would significantly enhance UX. |

## 4. Code Quality & Best Practices

### 4.1. Dependency Management
*   **Issue:** No `requirements.txt` file exists in the `app/` folder.
*   **Fix:** Create `app/requirements.txt` listing:
    ```text
    streamlit
    pandas
    numpy
    matplotlib
    seaborn
    MannKS  # or . (if installed from root)
    xlsxwriter # for excel support if needed
    ```

### 4.2. Reporting
*   **Issue:** The HTML report generation manually constructs HTML strings.
*   **Fix:** Use a templating engine like `jinja2` for cleaner, safer, and more maintainable report generation.

### 4.3. Error Handling in Plotting
*   **Issue:** If `MannKS` raises a warning (e.g., "High censoring"), it is captured in `analysis_notes` but might not be prominent enough.
*   **Fix:** Display `analysis_notes` as `st.warning` banners in the Results tab, not just as text in a table.

## 5. Concrete Action Plan

1.  **Fix `analysis.py`**: Update `run_analysis` to pass `x_input['value']` to `plot_seasonal_distribution`.
2.  **Update `settings.py`**:
    *   Convert `agg_period` inputs to SelectBoxes.
    *   Add `hicensor` checkbox.
3.  **Update `data_loader.py`**:
    *   Add "Censoring Type" (Left/Right) radio button for "Separate Flag" mode.
    *   Add "Date Format" input.
4.  **Enhance `results`**: Ensure Residual plots are displayed if generated.
5.  **Create `requirements.txt`**.
