"""
Tests for graph utils.
"""

import unittest

import numpy as np
from xland.utils import GRANULARITY, convert_to_actual_pos


class TestConvertToActualPos(unittest.TestCase):
    def test_convert_to_actual_pos(self):
        # Positions from 0 to 4, included
        positions = np.array([[0, 1], [0, 0]])
        grid_size = 5
        true_positions = np.array([x[0, 10], y[0, 10], [0, 0]])

        x = np.linspace(0, grid_size, grid_size * GRANULARITY)
        y = np.linspace(0, grid_size, grid_size * GRANULARITY)
        x, y = np.meshgrid(x, y)
        z = np.zeros(x.shape)
        half = grid_size * GRANULARITY // 2
        z[:half, :half] = 1
        new_pos = convert_to_actual_pos(positions, (x, y, z))


if __name__ == "__main__":
    unittest.main()
