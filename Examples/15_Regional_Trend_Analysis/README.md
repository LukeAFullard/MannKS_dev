# Example 15: Regional Trend Analysis

This example demonstrates how to use the `regional_test` function to aggregate trend results from multiple individual sites and determine if there is a statistically significant trend across the entire region.

## Key Concepts

Often, environmental data is collected from a network of monitoring sites. While analyzing the trend at each site is important, it's also valuable to understand the overall picture. A regional test answers the question: "Is there a general, region-wide trend, even if some individual sites show no trend or a trend in the opposite direction?"

The `MannKenSen.regional_test` function implements the method described by Helsel and Frans (2006), which involves the following steps:
1.  **Individual Tests:** Perform a standard `trend_test` (or `seasonal_trend_test`) for each site.
2.  **Sum S-statistics:** Sum the individual Mann-Kendall S-statistics from all sites.
3.  **Sum Variances:** Sum the variances of the S-statistics from all sites.
4.  **Covariance Adjustment:** Calculate the covariance between sites to account for inter-site correlation (i.e., sites that tend to vary together). This adjustment is added to the summed variance.
5.  **Regional Test:** Perform a final Z-test using the summed S-statistic and the adjusted summed variance to determine the overall regional trend.

## Script: `run_example.py`
The script simulates a common real-world scenario by generating data for three distinct monitoring sites:
-   **Site A:** Has a strong increasing trend.
-   **Site B:** Has a weaker, but still positive, increasing trend.
-   **Site C:** Has no trend (stable data).

The script then follows the regional analysis workflow:
1.  It loops through the data for each site and performs a standard `trend_test`.
2.  It collects these individual results into a list.
3.  It passes the list of results and the full dataset to the `regional_test` function to calculate the final, aggregated trend.

## Results

### Output Analysis (`regional_analysis_output.txt`)
The output file shows the step-by-step process.

1.  **Individual Results:** First, you see the `Mann_Kendall_Test` namedtuple printed for each of the three sites. You will likely see that Site A and Site B are "Increasing", while Site C is "No Trend".

2.  **Regional Result:** Following the individual results, the output of the `regional_test` is printed. This is a `Regional_Mann_Kendall_Test` namedtuple containing the final aggregated statistics. Despite the "No Trend" result from Site C, the regional test combines the evidence from all sites and correctly concludes that there is an overall "Increasing" trend for the region as a whole.

**Conclusion:** The `regional_test` function is a powerful tool for synthesizing trend information from multiple time series, providing a statistically sound method for assessing large-scale environmental changes.
