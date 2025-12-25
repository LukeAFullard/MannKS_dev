import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Add repo root to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from validation.validation_utils import ValidationUtils
import MannKenSen as mk

def generate_highly_tied_data(n=30):
    """Generates data with many ties."""
    dates = pd.date_range(start='2000-01-01', periods=n, freq='ME')
    # Step function
    values = np.zeros(n)
    values[10:20] = 5
    values[20:] = 10
    return pd.DataFrame({'date': dates, 'value': values})

def run():
    utils = ValidationUtils(os.path.dirname(__file__))

    df = generate_highly_tied_data()

    # 1. Standard Comparison (Tau-b default)
    utils.run_comparison(
        test_id="V-03",
        df=df,
        scenario_name="tau_b_comparison",
        mk_kwargs={'tau_method': 'b'}
    )
    utils.generate_plot(df, "V-03 Highly Tied Data", "v03_tied.png")

    # 2. Tau-a check
    utils.run_comparison(
        test_id="V-03",
        df=df,
        scenario_name="tau_a_comparison",
        mk_kwargs={'tau_method': 'a'}
    )

    # Generate Report
    utils.create_report()

if __name__ == "__main__":
    np.random.seed(42)
    run()
