# Changelog

## [0.6.0] - 2026-03-05

### Added
- **Surrogate Data Testing**: Robust hypothesis testing against colored noise backgrounds.
  - `surrogate_test` function supporting IAAFT (even sampling) and Lomb-Scargle (uneven sampling).
  - Handles censored data via rank-based censoring propagation.
  - Integration with `trend_test` and `seasonal_trend_test` via `surrogate_method`.
- **Power Analysis**: Monte Carlo power estimation for trend detection.
  - `power_test` calculates statistical power curves and Minimum Detectable Trend (MDT).
  - Supports custom noise models (IAAFT/Lomb-Scargle) and slope scaling.
- **Seasonal Integration**: Full support for surrogate testing in seasonal contexts.
  - Aggregates surrogate statistics across seasons.
  - Correctly handles argument alignment for seasonal subsets.
- **Dependencies**: Added `astropy` for spectral analysis and `piecewise-regression`.

### Fixed
- **Reproducibility**: Ensured `random_state` deterministically seeds all internal Monte Carlo loops in `power_test` and `surrogate_test`.

## [0.5.0] - 2026-03-04

### Added
- **Large Dataset Support**: Automatic handling of datasets with 10,000+ observations
  - Three-tiered system: Full (exact), Fast (approximate), Aggregate (recommended)
  - Stochastic Sen's slope estimation via random pair sampling
  - Stratified sampling for seasonal tests maintains season balance
  - New parameters: `large_dataset_mode`, `max_pairs`, `random_state`
  - Performance: 10x-100x faster for medium/large datasets
  - Accuracy: <0.5% error with default settings

### Changed
- Return tuple now includes: `computation_mode`, `pairs_used`, `approximation_error`
- Maximum safe dataset size increased from ~5,000 to ~50,000 (fast mode)
- Memory usage reduced significantly for large datasets

### Backwards Compatibility
- All existing code works unchanged
- Small datasets (n < 5000) use exact algorithms automatically
- No breaking changes to function signatures (only additions)
- All existing tests pass

### Documentation
- New guide: `Examples/Detailed_Guides/large_dataset_guide.md`
- Updated README with performance benchmarks
- Added examples for all three operational modes
