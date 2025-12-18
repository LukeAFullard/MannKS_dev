
# Example 15: Regional Trend Analysis

This example demonstrates how to use the `regional_test` function to aggregate trend results from multiple sites to determine if there is a significant trend across an entire region.

## Key Concepts
A regional test answers the question: "Is there a general, region-wide trend?" It works by:
1.  Performing a trend test on each individual site.
2.  Aggregating the S-statistics and their variances.
3.  Adjusting for inter-site correlation.
4.  Performing a final Z-test on the aggregated results.

## Script: `run_example.py`
The script simulates a scenario with three sites: two with increasing trends of different strengths and one with no trend. It analyzes each site individually and then passes the results to the `regional_test` function.

## Results
Despite one site showing no trend, the regional test combines the evidence to find an overall trend.

### Individual Site Results
- Site A Trend: Highly Likely Increasing\n
- Site B Trend: Highly Likely Increasing\n
- Site C Trend: No Trend\n

### Regional Test Result
- **Regional Trend Direction:** Increasing\n- **Aggregate Trend Confidence (CT):** 0.9985\n- **Number of Sites (M):** 3\n

**Conclusion:** The `regional_test` function provides a statistically sound method for assessing large-scale environmental changes by synthesizing trend information from multiple time series.
