"""
Seeding utils.
"""

import numpy as np


def seed_env(seed=None):
    # TODO: migrate to using rng keys
    if seed is not None:
        np.random.seed(seed)


def generate_seed():
    """
    Generate seeds to pass to the C++ side.
    """
    return np.random.randint(0, 2**32)
