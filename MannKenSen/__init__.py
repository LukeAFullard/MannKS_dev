"""
A Python package for non-parametric trend analysis of time series data.
"""
from .original_test import original_test
from .seasonal_test import seasonal_test
from .seasonality_test import seasonality_test
from .plotting import plot_seasonal_distribution

__all__ = [
    'original_test',
    'seasonal_test',
    'seasonality_test',
    'plot_seasonal_distribution',
]
