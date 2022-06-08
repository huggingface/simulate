"""
Tests for graph utils.
"""

import unittest

import numpy as np
from xland.utils import get_connected_components


class TestConnectedComponents(unittest.TestCase):
    def test_get_connected_components(self):

        edges = {
            0: [1, 2],
            1: [2],
            2: [0],
            3: [5, 2],
            4: [],
            5: [3],
        }

        n_nodes = 6

        true_components = [[4], [3, 5], [0, 1, 2]]

        components = get_connected_components(n_nodes, edges)
        components = [sorted(c) for c in components]

        # Check values
        self.assertEqual(len(components), len(true_components))
        for i in range(len(components)):
            self.assertTrue(expr=np.array_equal(components[i], true_components[i]))


if __name__ == "__main__":
    unittest.main()
