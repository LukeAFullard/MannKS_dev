
# Example 10: Handling Data with Multiple Censoring Levels

This example demonstrates the robustness of `MannKenSen` in handling complex, realistic datasets that contain numerous different censoring levels.

## Key Concepts
Real-world data often has a mix of censoring types (e.g., `<1`, `<5`, `>50`). The statistical engine in `MannKenSen` is designed to handle this complexity automatically. The standard workflow of `prepare_censored_data` followed by `trend_test` is sufficient. The test correctly interprets the relationships between all pairs of values, whether they are censored or not.

## Script: `run_example.py`
The script generates a synthetic dataset with an increasing trend and a complex mix of left-censored (`<1`, `<2`, `<5`) and right-censored (`>10`, `>15`) data. It runs the standard analysis workflow and generates this README.

## Results
The analysis correctly identifies the strong increasing trend despite the complex data.
- **Classification:** Highly Likely Increasing\n- **P-value:** 1.49e-04\n- **Annual Slope:** 1.0220\n- **Proportion Censored:** 40.00%\n

### Analysis Plot (`multi_censor_plot.png`)
The plot visualizes the complex data, using different markers for uncensored (circles), left-censored (downward triangles), and right-censored (upward triangles) data points.
![Multi-Censor Plot](multi_censor_plot.png)

**Conclusion:** `MannKenSen` is a robust tool for handling complex, messy, real-world censored data without requiring special configuration.
