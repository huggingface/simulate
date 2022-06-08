"""
Tests for setting objects on the map.
"""

import unittest

import numpy as np
from xland.world.set_object import get_connectivity_graph, get_object_pos, get_playable_area


class TestGraphBuilding(unittest.TestCase):
    def test_simple_graph(self):
        z = np.array(
            [
                [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]],
                [[0, 0, 0], [0, 2, 0], [1, 0, 0], [1, 0, 0]],
                [[0, 0, 0], [0, 0, 0], [2, 0, 0], [2, 0, 0]],
            ]
        )

        true_edges = {
            0: [1, 4],
            1: [0, 2],
            2: [1, 3],
            3: [2],
            4: [0, 5, 8],
            5: [1, 4, 6, 9],
            6: [2, 5, 7],
            7: [3, 6],
            8: [4, 9],
            9: [8],
            10: [6, 9, 11],
            11: [7, 10],
        }

        nodes, edges = get_connectivity_graph(z)
        edges = {n: sorted(e) for n, e in edges.items()}

        # Check values
        self.assertTrue(expr=np.array_equal(edges, true_edges))

    def test_ramps(self):
        z = np.array(
            [[[0, 0, 0], [0, 2, 0], [1, 0, 0]], [[3, 3, 0], [0, 0, 0], [1, 1, 0]], [[3, 0, 0], [2, 4, 0], [2, 0, 0]]]
        )

        true_edges = {
            0: [1],
            1: [0, 2, 4],
            2: [1, 5],
            3: [0, 4, 6],
            4: [],
            5: [2, 4, 8],
            6: [3, 7],
            7: [4, 6, 8],
            8: [5, 7],
        }

        nodes, edges = get_connectivity_graph(z)
        edges = {n: sorted(e) for n, e in edges.items()}

        # Check values
        self.assertTrue(expr=np.array_equal(edges, true_edges))


class TestGetPlayableArea(unittest.TestCase):
    def test_playable_area(self):
        z = np.array(
            [[[0, 0, 0], [0, 2, 0], [1, 0, 0]], [[3, 3, 0], [0, 0, 0], [1, 1, 0]], [[3, 0, 0], [2, 4, 0], [2, 0, 0]]]
        )
        true_area = 8 / 9

        playable_nodes, area = get_playable_area(z)
        self.assertAlmostEqual(area, true_area)


class TestSetObject(unittest.TestCase):
    def test_set_object(self):
        z = np.array(
            [[[0, 0, 0], [0, 2, 0], [1, 0, 0]], [[3, 3, 0], [0, 0, 0], [1, 1, 0]], [[3, 0, 0], [2, 4, 0], [2, 0, 0]]]
        )

        obj_pos, success = get_object_pos(z, 8)
        self.assertTrue(success)
        self.assertTrue(not (1, 1) in zip(*obj_pos))


if __name__ == "__main__":
    unittest.main()
