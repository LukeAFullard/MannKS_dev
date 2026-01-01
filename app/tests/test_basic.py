import pytest
from app.modules.data_generator import generate_synthetic_data

def test_generator():
    df = generate_synthetic_data(10, None, 'Days', 0.1, 0, 0, 0, 0, 0, 'None', 0, 42)
    assert len(df) == 10
    assert 'value' in df.columns
