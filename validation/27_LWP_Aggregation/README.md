# V-27: LWP Aggregation Verification

Comparison of Python `agg_method='lwp'` vs R `UseMidObs=TRUE`.

| Scenario              | Metric   | Python (LWP)   | R       | Match   |
|-----------------------|----------|----------------|---------|---------|
| Monthly Aggregation   | Slope    | 1.89486        | 1.89486 | ✅       |
| Monthly Aggregation   | P-Value  | 0.00000        | 0.00000 | ✅       |
| ---                   | ---      | ---            | ---     | ---     |
| Quarterly Aggregation | Slope    | 1.82811        | 1.82811 | ✅       |
| Quarterly Aggregation | P-Value  | 0.00000        | 0.00000 | ✅       |
| ---                   | ---      | ---            | ---     | ---     |