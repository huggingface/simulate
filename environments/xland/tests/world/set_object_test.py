"""
Tests for setting objects on the map.
"""

import unittest

import numpy as np
from xland.world.set_object import get_connectivity_graph, get_playable_area, get_positions


class TestGraphBuilding(unittest.TestCase):
    def test_simple_graph(self):
        z = np.array(
            [
                [[[0, 0], [0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0]]],
                [[[0, 0], [0, 0]], [[0, 1], [0, 1]], [[1, 1], [1, 1]], [[1, 1], [1, 1]]],
                [[[0, 0], [0, 0]], [[0, 0], [0, 0]], [[2, 2], [2, 2]], [[2, 2], [2, 2]]],
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

        true_lowest_plain_nodes = [0, 1, 2, 3, 4, 8, 9]

        n_plain_tiles = 11

        nodes, edges, plain_tiles, lowest_plain_nodes = get_connectivity_graph(z)
        edges = {n: sorted(e) for n, e in edges.items()}

        # Check values
        self.assertTrue(expr=np.array_equal(edges, true_edges))
        self.assertEqual(len(plain_tiles), n_plain_tiles)
        self.assertTrue(expr=np.array_equal(lowest_plain_nodes, true_lowest_plain_nodes))

    def test_simple_graph_second(self):
        z = np.array(
            [
                [[[2, 2], [2, 2]], [[1, 1], [1, 1]], [[2, 2], [2, 2]]],
                [[[2, 2], [2, 2]], [[1, 1], [1, 1]], [[2, 2], [2, 2]]],
                [[[2, 2], [2, 2]], [[1, 1], [1, 1]], [[2, 2], [2, 2]]],
            ]
        )

        true_edges = {
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

        true_lowest_plain_nodes = [1, 4, 7]

        n_plain_tiles = 9

        nodes, edges, plain_tiles, lowest_plain_nodes = get_connectivity_graph(z)
        edges = {n: sorted(e) for n, e in edges.items()}
        playable_nodes, area = get_playable_area(z, enforce_lower_floor=False)

        # Check values
        self.assertTrue(expr=np.array_equal(edges, true_edges))
        self.assertEqual(len(plain_tiles), n_plain_tiles)
        self.assertTrue(expr=np.array_equal(lowest_plain_nodes, true_lowest_plain_nodes))

    def test_ramps(self):
        z = np.array(
            [
                [[[0, 0], [0, 0]], [[0, 1], [0, 1]], [[1, 1], [1, 1]]],
                [[[4, 4], [3, 3]], [[0, 0], [0, 0]], [[1, 1], [2, 2]]],
                [[[3, 3], [3, 3]], [[3, 2], [3, 2]], [[2, 2], [2, 2]]],
            ]
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

        true_lowest_plain_nodes = [0, 4]

        n_plain_tiles = 5

        nodes, edges, plain_tiles, lowest_plain_nodes = get_connectivity_graph(z)
        edges = {n: sorted(e) for n, e in edges.items()}

        # Check values
        self.assertTrue(expr=np.array_equal(edges, true_edges))
        self.assertEqual(len(plain_tiles), n_plain_tiles)
        self.assertTrue(expr=np.array_equal(lowest_plain_nodes, true_lowest_plain_nodes))


class TestGetPlayableArea(unittest.TestCase):
    def test_playable_area(self):
        z = np.array(
            [
                [[[0, 0], [0, 0]], [[0, 1], [0, 1]], [[1, 1], [1, 1]]],
                [[[4, 4], [3, 3]], [[0, 0], [0, 0]], [[1, 1], [2, 2]]],
                [[[3, 3], [3, 3]], [[3, 2], [3, 2]], [[2, 2], [2, 2]]],
            ]
        )
        true_area = 8 / 9

        playable_nodes, area = get_playable_area(z, enforce_lower_floor=False)
        self.assertAlmostEqual(area, true_area)


class TestSetObject(unittest.TestCase):
    def test_set_object(self):
        z = np.array(
            [
                [[[0, 0], [0, 0]], [[0, 1], [0, 1]], [[1, 1], [1, 1]]],
                [[[4, 4], [3, 3]], [[0, 0], [0, 0]], [[1, 1], [2, 2]]],
                [[[3, 3], [3, 3]], [[3, 2], [3, 2]], [[2, 2], [2, 2]]],
            ]
        )

        obj_pos, agent_pos, success = get_positions(z, 4, 0, enforce_lower_floor=False)
        self.assertTrue(success)
        self.assertTrue(not (1, 1) in zip(*obj_pos))
        self.assertTrue(not (0, 1) in zip(*obj_pos))
        self.assertTrue(not (1, 0) in zip(*obj_pos))
        self.assertTrue(not (1, 2) in zip(*obj_pos))
        self.assertTrue(not (2, 1) in zip(*obj_pos))


if __name__ == "__main__":
    unittest.main()
