
import numpy as np
import pandas as pd
from typing import Union, Optional

def check_data_integrity(
    x: Union[np.ndarray, "pd.DataFrame"],
    t: np.ndarray,
    context: str = "analysis"
) -> None:
    """
    Validates input data for statistical tests, ensuring it meets requirements for
    robust execution (no NaNs, no Infs, sufficient sample size).

    Args:
        x (Union[np.ndarray, pd.DataFrame]): Data values.
        t (np.ndarray): Time values.
        context (str): Context of the check (e.g., 'surrogate_test', 'power_test') for error messages.

    Raises:
        ValueError: If data contains NaNs, Infs, or is insufficient.
    """
    x_arr = np.asarray(x).flatten()
    t_arr = np.asarray(t).flatten()

    # Check for NaNs
    if np.isnan(x_arr).any():
        raise ValueError(
            f"Input `x` contains NaNs. The {context} requires complete data. "
            "Please filter your data using `dropna()` or similar methods before running this test."
        )
    if np.isnan(t_arr).any():
        raise ValueError(
            f"Input `t` contains NaNs. The {context} requires valid timestamps for all observations."
        )

    # Check for Infinite values
    if not np.isfinite(x_arr).all():
        raise ValueError(
            f"Input `x` contains infinite values. The {context} requires finite numerical data."
        )
    if not np.isfinite(t_arr).all():
        raise ValueError(
            f"Input `t` contains infinite values. The {context} requires finite timestamps."
        )

    # Check for Sample Size
    if len(x_arr) < 3:
        # Contextual relaxation: For internal seasonal surrogate tests, n=2 might be passed.
        # We allow it but warn, or rely on the caller to handle degenerate cases.
        # However, for general analysis, < 3 is usually insufficient.
        # Given that seasonal_trend_test calls surrogate_test for n > 1, we must allow n=2
        # to prevent crashes in that loop.
        if len(x_arr) < 2:
            raise ValueError(
                f"Insufficient data for {context} (n={len(x_arr)}). "
                "At least 2 observations are required."
            )
        # If n=2, we proceed (S statistic is defined).
        pass

    # Check for Constant Data (Warning? Or just allow it?)
    # Constant data is valid but degenerate. surrogate_test handles it (p=1.0).
    # We won't raise an error here, but it's good to know.
