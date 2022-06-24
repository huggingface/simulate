"""
Seeding utils.
"""

import numpy as np


def seed_env(seed=None):
    # TODO: migrate to using rng keys
    if seed is not None:
        np.random.seed(seed)
