
# Example 11: Advanced Seasonality (Non-Monthly Data)

This example demonstrates the flexibility of `MannKenSen`'s seasonal analysis for non-monthly data, such as a weekly (`day_of_week`) pattern.

## Key Concepts
Seasonal analysis is not limited to monthly data. The `season_type` parameter in `seasonal_trend_test` and `plot_seasonal_distribution` allows analysis of any sub-annual pattern (e.g., weekly, quarterly) by correctly grouping the data.

## Script: `run_example.py`
The script generates a 3-year daily dataset with a strong weekly cycle (higher values on weekends) and an underlying increasing trend. It then visualizes the weekly pattern and performs a seasonal trend test using `season_type='day_of_week'`.

## Results
The test successfully isolates the long-term trend from the weekly cycle.
- **Classification:** Highly Likely Increasing\n- **P-value:** 0.00e+00\n- **Annual Slope:** 5.1989\n

### Seasonal Distribution Plot (`seasonal_distribution_plot.png`)
This plot clearly shows the weekly cycle, with higher values for day 5 (Saturday) and 6 (Sunday).
![Seasonal Distribution Plot](seasonal_distribution_plot.png)

### Seasonal Trend Plot (`seasonal_trend_plot.png`)
The trend plot shows the overall time series and correctly identifies the underlying increasing trend.
![Seasonal Trend Plot](seasonal_trend_plot.png)

**Conclusion:** The `season_type` parameter makes `seasonal_trend_test` a versatile tool for analyzing time series data with various cyclical patterns.
