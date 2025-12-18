
# Example 7: The High Censor Rule (`hicensor`)

This example demonstrates the `hicensor` rule, a feature for handling data where detection limits have improved over time, which can create a misleading "paper trend".

## Key Concepts

If a lab's detection limit improves (e.g., from `<10` to `<1`), data may appear to have a decreasing trend even if the true values are stable. The `hicensor` rule corrects for this. When `hicensor=True`, the function finds the highest detection limit (e.g., `10`) and treats all values below this limit as being censored at that limit (e.g., `<1` and `<5` both become `<10`).

## Script: `run_example.py`
The script generates a dataset where the recorded values decrease over time solely because the detection limit is improving. It analyzes the data twice: once without the `hicensor` rule and once with it.

## Results

### Analysis Without `hicensor` Rule
While a visual inspection of the raw values (10, 5, 2, 1) might suggest a trend, the robust statistical test correctly handles comparisons between different censored levels (e.g., `<10` vs. `<5`) as ambiguous ties.
- **Classification:** No Trend\n- **P-value:** 1.0\n- **S-statistic:** 0.0\n
![Original Data Plot](original_data_plot.png)

### Analysis With `hicensor` Rule
Applying the `hicensor` rule formalizes the analysis by standardizing all data to the highest detection limit. This confirms the 'No Trend' result.
- **Classification:** No Trend\n- **P-value:** 1.0\n- **S-statistic:** 0.0\n
![Hicensor Rule Plot](hicensor_rule_plot.png)

**Conclusion:** The `hicensor` rule is a key tool for validating trend analysis on long-term datasets where analytical methods may have changed.
