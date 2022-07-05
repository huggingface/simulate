"""
Builds map using Wave Function Collapse.
"""

import numpy as np

from ..constants import GRANULARITY
from .wfc_utils import generate_seed
from .wfc_wrapping import apply_wfc


def generate_2d_map(
    width,
    height,
    periodic_output=True,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=1,
    sample_map=None,
    verbose=False,
    tiles=None,
    neighbors=None,
    symmetries=None,
    weights=None,
):
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
    width=9,
    height=9,
    periodic_output=False,
    final_tile_size=1,
    specific_map=None,
    sample_map=None,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=1,
    verbose=False,
    tiles=None,
    neighbors=None,
    symmetries=None,
    weights=None,
):
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
            larger than one might imply in new tiles, which might be a unwanted behaviour
            (WFC param).
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
    true_nb_samples = samples.shape[0]
    width = samples.shape[1]
    height = samples.shape[2]

    def build_single_map(sample):
        # We create the mesh centered in (0,0)
        x = np.linspace(-height / 2, height / 2, GRANULARITY * height)
        z = np.linspace(-width / 2, width / 2, GRANULARITY * width)

        # Create mesh grid
        x, z = np.meshgrid(x, z)

        # Here, we create the mesh
        # As we are using tiles of two by two, first we have to find a interpolation on
        # the x axis for each tile
        # and then on the y axis for each tile
        # In order to do so, we can use np.linspace, and then transpose the tensor and
        # get the right order
        y = np.linspace(sample[:, :, :, 0], sample[:, :, :, 1], GRANULARITY)
        y = np.linspace(y[:, :, :, 0], y[:, :, :, 1], GRANULARITY)
        y = np.transpose(y, (2, 0, 3, 1)).reshape((width * GRANULARITY, height * GRANULARITY), order="A")

        coordinates = np.stack([x, y, z])

        return coordinates

    all_coordinates = [build_single_map(samples[i]) for i in range(true_nb_samples)]
    return all_coordinates, samples
