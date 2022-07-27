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

    def test_get_connected_components_second(self):

        edges = {
            0: [1, 3],
            1: [4],
            2: [1, 5],
            3: [0, 4, 6],
            4: [1, 7],
            5: [2, 4, 8],
            6: [3, 7],
            7: [4],
            8: [5, 7],
        }

        n_nodes = 9

        true_components = [[2, 5, 8], [0, 3, 6], [1, 4, 7]]

        components = get_connected_components(n_nodes, edges)
        components = [sorted(c) for c in components]

        # Check values
        self.assertEqual(len(components), len(true_components))
        for i in range(len(components)):
            self.assertTrue(expr=np.array_equal(components[i], true_components[i]))


if __name__ == "__main__":
    unittest.main()
