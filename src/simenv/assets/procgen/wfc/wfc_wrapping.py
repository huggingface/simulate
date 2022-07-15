"""Python wrapper for constructors of C++ classes."""

import numpy as np

from wfc_binding import build_neighbor, build_tile, run_wfc, transform_to_id_pair


def build_wfc_neighbor(left, right, left_or=0, right_or=0):
    """
    Builds neighbors.
    """
    return build_neighbor(left=bytes(left, "UTF_8"), left_or=left_or, right=bytes(right, "UTF_8"), right_or=right_or)


def build_wfc_tile(tile, name, symmetry="L", weight=1, size=0):
    """
    Builds tiles.
    """
    return build_tile(
        size=size, tile=tile, name=bytes(name, "UTF_8"), symmetry=bytes(symmetry, "UTF_8"), weight=weight
    )


def preprocess_tiles(tiles, symmetries=None, weights=None):
    n_tiles, tile_w, tile_h = tiles.shape
    tile_shape = tile_w, tile_h

    if symmetries is None:
        symmetries = ["L"] * n_tiles

    if weights is None:
        weights = [1] * n_tiles

    tiles = [tuple(map(tuple, tile)) for tile in tiles]

    idx_to_tile = {i: tiles[i] for i in range(n_tiles)}
    tile_to_idx = {tiles[i]: i for i in range(n_tiles)}

    converted_tiles = [
        build_wfc_tile(
            size=1,
            tile=[i],
            name=str(i),
            symmetry=symmetries[i],
            weight=weights[i],
        )
        for i in range(n_tiles)
    ]

    return converted_tiles, idx_to_tile, tile_to_idx, tile_shape


def preprocess_neighbors(neighbors, tile_to_idx):
    """
    Preprocesses tiles.
    """
    preprocessed_neighbors = []

    for neighbor in neighbors:
        preprocessed_neighbor = (
            str(tile_to_idx[tuple(map(tuple, neighbor[0]))]),
            str(tile_to_idx[tuple(map(tuple, neighbor[1]))]),
            *neighbor[2:],
        )

        preprocessed_neighbors.append(build_wfc_neighbor(*preprocessed_neighbor))

    return preprocessed_neighbors


def preprocess_tiles_and_neighbors(tiles, neighbors, symmetries=None, weights=None):
    """
    Preprocesses tiles.
    """
    converted_tiles, idx_to_tile, tile_to_idx, tile_shape = preprocess_tiles(tiles, symmetries, weights)
    converted_neighbors = preprocess_neighbors(neighbors, tile_to_idx)

    return converted_tiles, converted_neighbors, idx_to_tile, tile_shape


def preprocess_input_img(input_img):
    """
    Preprocesses input image by extracting the tiles.
    """
    w, h, tile_w, tile_h = input_img.shape
    tile_shape = tile_w, tile_h
    input_img = np.reshape(input_img, (-1, tile_w, tile_h))
    tuple_input_img = [tuple(map(tuple, tile)) for tile in input_img]

    tile_to_idx = {}
    idx_to_tile = {}

    counter = 0
    for i in range(w * h):
        if tuple_input_img[i] not in tile_to_idx:
            tile_to_idx[tuple_input_img[i]] = counter
            idx_to_tile[counter] = input_img[i]
            counter += 1

    converted_input_img = [transform_to_id_pair(tile_to_idx[tile]) for tile in tuple_input_img]

    return converted_input_img, idx_to_tile, tile_shape


def get_tiles_back(gen_map, tile_conversion, nb_samples, width, height, tile_shape):
    """
    Returns tiles back.
    """
    gen_map = np.reshape(gen_map, (nb_samples * width * height, 3))
    converted_map = []

    for i in range(nb_samples * width * height):
        # Rotate and reflect single tiles / patterns
        converted_tile = np.rot90(tile_conversion[gen_map[i][0]], gen_map[i][1])
        if gen_map[i][2] == 1:
            converted_tile = np.fliplr(converted_tile)
        converted_map.append(converted_tile)

    return np.reshape(np.array(converted_map), (nb_samples, width, height, *tile_shape))


def apply_wfc(
    width,
    height,
    input_img=None,
    tiles=None,
    neighbors=None,
    periodic_output=True,
    N=3,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=8,
    seed=0,
    verbose=False,
    nb_tries=100,
    symmetries=None,
    weights=None,
):
    if (tiles is not None and neighbors is not None) or input_img is not None:
        if input_img is not None:
            input_width, input_height = input_img.shape[:2]
            input_img, tile_conversion, tile_shape = preprocess_input_img(input_img)
            sample_type = 1

        else:
            input_width, input_height = 0, 0
            tiles, neighbors, tile_conversion, tile_shape = preprocess_tiles_and_neighbors(
                tiles, neighbors, symmetries, weights
            )
            sample_type = 0

        gen_map = run_wfc(
            width=width,
            height=height,
            sample_type=sample_type,
            input_img=input_img,
            input_width=input_width,
            input_height=input_height,
            periodic_output=periodic_output,
            N=N,
            periodic_input=periodic_input,
            ground=ground,
            nb_samples=nb_samples,
            symmetry=symmetry,
            seed=seed,
            verbose=verbose,
            nb_tries=nb_tries,
            tiles=tiles,
            neighbors=neighbors,
        )

        gen_map = get_tiles_back(gen_map, tile_conversion, nb_samples, width, height, tile_shape)
        return gen_map

    else:
        raise ValueError("Either input_img or tiles and neighbors must be provided.")
