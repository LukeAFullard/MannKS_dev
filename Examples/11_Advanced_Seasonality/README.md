# Example 11: Advanced Seasonality (Non-Monthly Data)

This example demonstrates the flexibility of the seasonal trend analysis functions in `MannKenSen`. While monthly data is common, seasonal patterns can occur over any sub-annual period, such as daily, weekly, or quarterly. The `season_type` parameter in `seasonal_trend_test` and `plot_seasonal_distribution` allows you to analyze these different cycles.

## Key Concepts

The `seasonal_trend_test` function is not hardcoded for monthly analysis. It uses the `season_type` parameter to internally group the time series data before performing the trend test. Some common `season_type` options include:
-   `'month'` (Default)
-   `'day_of_week'`
-   `'quarter'`
-   `'day_of_year'`
-   `'hour'`

By specifying the correct `season_type`, you can isolate a long-term trend from any regular, repeating cycle in your data. This example focuses on a `day_of_week` pattern, which is common in many types of data (e.g., traffic, energy consumption, air quality).

## Script: `run_example.py`
The script generates a three-year daily dataset with two key features:
1.  A strong **weekly seasonal pattern**, with higher values on weekends (Saturday and Sunday) compared to weekdays.
2.  A clear, underlying **increasing long-term trend**.

The script first visualizes the weekly pattern using `plot_seasonal_distribution` and then uses `seasonal_trend_test` with `season_type='day_of_week'` to calculate the long-term trend.

## Results

### Seasonal Distribution Plot (`seasonal_distribution_plot.png`)
This plot clearly shows the weekly cycle, with significantly higher values for day 5 (Saturday) and day 6 (Sunday) compared to the other days.
![Seasonal Distribution Plot](seasonal_distribution_plot.png)

### Seasonal Trend Plot (`seasonal_trend_plot.png`)
The trend plot shows the overall time series and correctly identifies the underlying increasing trend, successfully separating it from the weekly noise.
![Seasonal Trend Plot](seasonal_trend_plot.png)


### Output Analysis (`advanced_seasonality_output.txt`)
The text output confirms the "Highly Likely Increasing" trend and provides the calculated Sen's slope. By analyzing the trend for each day of the week separately, the function avoids being misled by the large, regular jumps in value that occur every weekend.

**Conclusion:** The `season_type` parameter makes `seasonal_trend_test` a versatile tool for a wide range of time series data, allowing you to find the true long-term trend in the presence of various cyclical patterns.
