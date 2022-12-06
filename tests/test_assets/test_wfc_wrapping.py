"""Tests of WFC wrapping functions."""

import unittest

import numpy as np

from simulate.assets.procgen.wfc.wfc_wrapping import (
    apply_wfc,
    preprocess_input_img,
    preprocess_tiles,
    preprocess_tiles_and_neighbors,
)


class TestTilesNeighbors(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tiles = np.array([[[0, 1], [1, 0]], [[2, 0], [0, 1]], [[0, 3], [0, 0]], [[0, 0], [0, 0]]])
        tile_names = [str(i) for i in range(len(tiles))]

        self.tiles = [{"name": name, "image": tile } for name, tile in zip(tile_names, tiles)]

        self.neighbors = [
            (self.tiles[0]["name"], self.tiles[1]["name"], 0, 1),
            (self.tiles[0]["name"], self.tiles[2]["name"], 1, 0),
            (self.tiles[0]["name"], self.tiles[3]["name"]),
            (self.tiles[1]["name"], self.tiles[2]["name"], 2, 2),
            (self.tiles[1]["name"], self.tiles[3]["name"]),
            (self.tiles[2]["name"], self.tiles[3]["name"]),
        ]

    def test_create_tiles(self):
        converted_tiles, tile_shape = preprocess_tiles(self.tiles)
        
        self.assertTrue(len(converted_tiles) == len(self.tiles))

        self.assertTrue(np.all([converted_tiles[i].name == str(i) for i in range(len(self.tiles))]))
        self.assertTrue(np.all([converted_tiles[i].name == str(i) for i in range(len(self.tiles))]))
        self.assertTrue(np.all([converted_tiles[i].symmetry == "L" for i in range(len(self.tiles))]))
        self.assertTrue(tile_shape == (2, 2))

    def test_create_tiles_neighbors(self):
        converted_tiles, converted_neighbors, tile_shape = preprocess_tiles_and_neighbors(self.tiles, self.neighbors)
        left_values = ["0", "0", "0", "1", "1", "2"]
        right_values = ["1", "2", "3", "2", "3", "3"]
        left_or_values = [0, 1, 0, 2, 0, 0]
        right_or_values = [1, 0, 0, 2, 0, 0]

        self.assertTrue(np.all([converted_neighbors[i].left == left_values[i] for i in range(len(self.neighbors))]))
        self.assertTrue(np.all([converted_neighbors[i].right == right_values[i] for i in range(len(self.neighbors))]))
        self.assertTrue(np.all([converted_neighbors[i].left_or == left_or_values[i] for i in range(len(self.neighbors))]))
        self.assertTrue(np.all([converted_neighbors[i].right_or == right_or_values[i] for i in range(len(self.neighbors))]))
        self.assertTrue(tile_shape == (2, 2))

    def test_apply_wfc_tiles(self):
        tiles = np.array([[[0, 0], [0, 0]], [[2, 0], [0, 1]]])
        tile_names = [str(i) for i in range(len(tiles))]

        tiles = [{"name": name, "image": tile } for name, tile in zip(tile_names, tiles)]
        neighbors = [
            (tiles[0]["name"], tiles[0]["name"]),
            (tiles[1]["name"], tiles[1]["name"]),
            (tiles[0]["name"], tiles[1]["name"]),
        ]
        width, height = 3, 3
        seed = np.random.randint(2**32)
        nb_samples = 1
        tile_shape = (2, 2)

        output = apply_wfc(
            width=width,
            height=height,
            periodic_output=False,
            seed=seed,
            verbose=False,
            tiles=tiles,
            neighbors=neighbors,
            nb_samples=nb_samples,
        )

        self.assertTrue(output.shape == (nb_samples, width, height, *tile_shape))


class TestSampleMap(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.y = np.array(
            [
                [[[0, 0], [0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0]]],
                [[[0, 0], [0, 0]], [[0, 2], [0, 0]], [[1, 0], [0, 0]], [[1, 0], [0, 0]]],
                [[[0, 0], [0, 0]], [[0, 0], [0, 0]], [[2, 0], [0, 0]], [[2, 0], [0, 0]]],
            ]
        )

    def test_sample_map(self):
        tuple_y = [tuple(map(tuple, tile)) for tile in np.reshape(self.y, (-1, 2, 2))]
        single_tiles = [tuple_y[0], tuple_y[5], tuple_y[6], tuple_y[10]]

        n_idxs = 4

        converted_input_img, idx_to_tile, tile_shape = preprocess_input_img(self.y)

        self.assertTrue(np.all([idx_to_tile[i] == single_tiles[i] for i in range(n_idxs)]))
        self.assertTrue(tile_shape == (2, 2))

    def test_apply_wfc_sample_map(self):
        width, height = 3, 3
        seed = np.random.randint(2**32)
        nb_samples = 1
        tile_shape = (2, 2)

        output = apply_wfc(
            width=width,
            height=height,
            periodic_output=False,
            seed=seed,
            input_img=self.y,
            verbose=False,
            nb_samples=nb_samples,
        )

        self.assertTrue(output.shape == (nb_samples, width, height, *tile_shape))


# if __name__ == "__main__":
#     unittest.main()
