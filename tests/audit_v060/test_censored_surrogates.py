
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from MannKS._surrogate import surrogate_test

def test_censored_flag_propagation():
    """
    Verify that censoring flags are correctly propagated to surrogates based on rank.
    """
    # Create a small dataset
    # Values: [10, 20, 30, 40, 50]
    # Censored: [T,  F,  F,  F,  T]
    # CenType:  [lt, not,not,not, lt]
    # Imputed (0.5x): [5, 20, 30, 40, 25] -> Sorted Imputed: [5, 20, 25, 30, 40]
    # Corresponding original ranks:
    # 5  (from idx 0, cen=T) -> Rank 0
    # 20 (from idx 1, cen=F) -> Rank 1
    # 25 (from idx 4, cen=T) -> Rank 2
    # 30 (from idx 2, cen=F) -> Rank 3
    # 40 (from idx 3, cen=F) -> Rank 4

    # So if a surrogate value has Rank 0 (lowest in surrogate), it should inherit cen=T.
    # If it has Rank 2, it should inherit cen=T.
    # Others cen=F.

    x = np.array([10, 20, 30, 40, 50])
    t = np.arange(5)
    censored = np.array([True, False, False, False, True])
    cen_type = np.array(['lt', 'not', 'not', 'not', 'lt'], dtype=object)

    # Mock the internal MK score function to inspect calls
    with patch('MannKS._surrogate._mk_score_and_var_censored') as mock_mk:
        # Mock return value to avoid crashes (dummy values)
        # Returns: S, var_s, denominator, tau
        mock_mk.return_value = (0, 1, 1, 0)

        # Run surrogate test
        # force iaaft for simplicity
        surrogate_test(
            x, t, censored=censored, cen_type=cen_type,
            method='iaaft', n_surrogates=1, random_state=42,
            lt_mult=0.5
        )

        # Verify calls.
        # Call 0: Original data
        # Call 1: Surrogate 0

        assert mock_mk.call_count >= 2

        # Check Surrogate call (last call)
        args, kwargs = mock_mk.call_args

        surr_x = args[0]
        surr_cen = kwargs['censored']

        # Verify mapping logic manually
        # 1. Get ranks of surrogate
        ranks = np.argsort(np.argsort(surr_x))

        # 2. Expected censoring based on our manual derivation
        # Ranks 0 and 2 should be censored.
        expected_cen_indices = [0, 2] # in terms of RANK

        # Check if the surrogate's censored array matches the rank expectation
        # We need to find which indices in surr_x correspond to rank 0 and 2

        for i in range(5):
            rank = ranks[i]
            if rank in expected_cen_indices:
                assert surr_cen[i] == True, f"Surrogate value at rank {rank} should be censored"
            else:
                assert surr_cen[i] == False, f"Surrogate value at rank {rank} should NOT be censored"
