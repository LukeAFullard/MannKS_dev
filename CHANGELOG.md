# Changelog

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
