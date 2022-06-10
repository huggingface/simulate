"""
Tests for graph utils.
"""

import unittest

import numpy as np
from xland.utils import convert_to_actual_pos


class TestConvertToActualPos(unittest.TestCase):
    def test_convert_to_actual_pos(self):
        # Positions from 0 to 4, included
        positions = np.array([[0, 1, 2], [2, 3, 4]])
        grid_size = 5

        x = np.linspace(0, grid_size, grid_size * 10)
        y = np.linspace(0, grid_size, grid_size * 10)
        x, y = np.meshgrid(x, y)

        z = np.arange(np.prod(x.shape), dtype=float).reshape(x.shape)

        # Answer
        idxs = ([4, 14, 24], [24, 34, 44])
        true_pos = np.array([x[idxs], y[idxs], z[idxs]]).transpose()

        # Calculated positions
        new_pos = convert_to_actual_pos(positions, (x, y, z))

        for i in range(len(idxs)):
            for j in range(3):
                self.assertAlmostEqual(true_pos[j, i], new_pos[j, i])


if __name__ == "__main__":
    unittest.main()
