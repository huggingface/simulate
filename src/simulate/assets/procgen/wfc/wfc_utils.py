"""
Utils function for Wave function collapse.
"""

import numpy as np


def generate_seed() -> int:
    """
    Generate seeds to pass to the C++ side.
    """
    return np.random.randint(0, 2**32, dtype=np.uint32)
