"""
Builds map using Wave Function Collapse.
"""

from typing import List, Optional, Tuple

import numpy as np

from ..constants import TILE_SIZE
from .wfc_utils import generate_seed
from .wfc_wrapping import apply_wfc


def generate_2d_map(
    width: int,
    height: int,
    periodic_output: bool = True,
    N: int = 2,
    periodic_input: bool = False,
    ground: bool = False,
    nb_samples: int = 1,
    symmetry: int = 1,
    sample_map: Optional[np.ndarray] = None,
    verbose: bool = False,
    tiles: Optional[np.ndarray] = None,
    neighbors: Optional[np.ndarray] = None,
    symmetries: Optional[np.ndarray] = None,
    weights: Optional[np.ndarray] = None,
) -> Optional[np.ndarray]:
    """
    Generate 2d map.

    Generation types with WFC:
    - Overlapping routine:
        - Creates a new map from a previous one by sampling patterns from it
    - Simpletiled routine:
        - Builds map from generated tiles and respective constraints

    Args:
        More information on the Args can be found on generate_map below.

    Returns:
        image: PIL image
    """

    # Generate seed for C++
    seed = generate_seed()

    # Call WFC function:
    return apply_wfc(
        width=width,
        height=height,
        input_img=sample_map,
        tiles=tiles,
        neighbors=neighbors,
        symmetries=symmetries,
        weights=weights,
        periodic_output=periodic_output,
        N=N,
        periodic_input=periodic_input,
        ground=ground,
        nb_samples=nb_samples,
        symmetry=symmetry,
        seed=seed,
        verbose=verbose,
    )


def generate_map(
    width: int = 9,
    height: int = 9,
    periodic_output: bool = False,
    final_tile_size: int = 1,
    specific_map: Optional[np.ndarray] = None,
    sample_map: Optional[np.ndarray] = None,
    N: int = 2,
    periodic_input: bool = False,
    ground: bool = False,
    nb_samples: int = 1,
    symmetry: int = 1,
    verbose: bool = False,
    tiles: Optional[np.ndarray] = None,
    neighbors: Optional[np.ndarray] = None,
    symmetries: Optional[np.ndarray] = None,
    weights: Optional[np.ndarray] = None,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """
    Generate the map.

    Args:
        width: The width of the map.
        height: The height of the map.
        periodic_output: Whether the output should be toric (WFC param).
        final_tile_size: The size of the resulting tiles.
        specific_map: if not None, use this map instead of generating one.
        sample_map: if not None, use this map as a sample from.
        N: size of patterns to be used by WFC.
        periodic_input: Whether the input is toric (WFC param).
        ground: Whether to use the lowest middle pattern to initialize the bottom of the map (WFC param).
        nb_samples: Number of samples to generate at once (WFC param).
        symmetry: Levels of symmetry to be used when sampling from a map. Values
            larger than one might imply in new tiles, which might be an unwanted behaviour
            (WFC param).
        verbose: Whether to print information about the generation process.
        tiles: List of tiles to be used by WFC.
        neighbors: List of neighbors to be used by WFC.
        symmetries: List of symmetries to be used by WFC.
        weights: List of weights to be used by WFC.
    """

    if specific_map is not None:
        # Adding samples dimension:
        samples = np.expand_dims(specific_map, axis=0)

    else:
        samples = generate_2d_map(
            width,
            height,
            sample_map=sample_map,
            periodic_output=periodic_output,
            N=N,
            periodic_input=periodic_input,
            ground=ground,
            nb_samples=nb_samples,
            symmetry=symmetry,
            verbose=verbose,
            tiles=tiles,
            neighbors=neighbors,
            symmetries=symmetries,
            weights=weights,
        )

    # Get the dimensions of map - since if plotting a specific_map, we might have different ones
    true_nb_samples, width, height, tile_width, tile_height = samples.shape

    def build_single_map(sample: np.ndarray) -> np.ndarray:
        # We create the mesh centered in (0,0)
        x = np.zeros((tile_height * height))
        z = np.zeros((tile_width * width))

        # TODO: optimize these two loops
        for i in range(height):
            for j in range(tile_height):
                x[tile_height * i + j] = TILE_SIZE * (-height / 2 + i + j / (tile_height - 1))

        for i in range(width):
            for j in range(tile_width):
                z[tile_width * i + j] = TILE_SIZE * (i - width / 2 + j / (tile_width - 1))

        # Create mesh grid
        x, z = np.meshgrid(x, z)

        # Here, we must get the y values
        # Basically, we just have to take the map which is of shape (width, height, tile_width, tile_height)
        # and transform it into (width * tile_width, height * tile_height) reshaping properly
        y = np.hstack(np.hstack(sample))
        coordinates = np.stack([x, y, z])

        return coordinates

    all_coordinates = [build_single_map(samples[i]) for i in range(true_nb_samples)]
    return all_coordinates, samples
