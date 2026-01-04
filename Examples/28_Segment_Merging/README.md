# Example 28: Merging Similar Segments

This example demonstrates how the `merge_similar_segments=True` option can simplify a model where the standard BIC criterion might select 'spurious' breakpoints due to noise or minor irregularities.

## 1. The Data
We generated synthetic data representing a single constant trend (Slope=1.0) with a noise 'bump' in the middle. This pattern often tricks statistical criteria into fitting multiple segments.

## 2. Before Merging (Standard BIC)
The standard analysis identified **2** breakpoints.

![Before Merging](plot_before.png)

### Segment Details
|    |    slope |   lower_ci |   upper_ci |
|---:|---------:|-----------:|-----------:|
|  0 | 0.953524 |   0.90358  |   0.997333 |
|  1 | 1.33342  |   1.04869  |   1.57051  |
|  2 | 0.914887 |   0.890638 |   0.942101 |

## 3. After Merging (Hypothesis Test)
We enabled `merge_similar_segments=True`. The algorithm checked adjacent segments. If their slope confidence intervals overlapped, they were considered indistinguishable, and the model was simplified.

The final merged model identified **1** breakpoints.

![After Merging](plot_after.png)

### Segment Details
|    |    slope |   lower_ci |   upper_ci |
|---:|---------:|-----------:|-----------:|
|  0 | 1.06913  |   1.02095  |   1.10969  |
|  1 | 0.928528 |   0.891417 |   0.966938 |

## Conclusion
The merging process successfully removed unnecessary breakpoints, simplifying the model structure.