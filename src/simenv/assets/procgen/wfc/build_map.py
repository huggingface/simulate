"""
Builds map using Wave Function Collapse.
"""

import os

import numpy as np

from wfc_binding import run_wfc

from .utils import GRANULARITY, decode_rgb, generate_seed


def generate_2d_map(
    width,
    height,
    periodic_output=True,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=1,
    sample_from=None,
    seed=None,
    verbose=False,
    tiles=None,
    neighbors=None,
):
    """
    Generate 2d map.

    Args:
        More information on the Args can be found on generate_map below.

    Returns:
        image: PIL image
    """

    # Otherwise, generate it
    if sample_from is not None:
        # Overlapping routine
        # Creates a new map from a previous one by sampling patterns from it
        # Need to transform string into bytes for the c++ function

        input_width, input_height, _ = sample_from.shape
        return run_wfc(
            width=width,
            height=height,
            sample_type=1,
            input_img=sample_from.reshape(input_width * input_height, -1).tolist(),
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
        )

    # Simpletiled routine
    # Builds map from generated tiles and respective constraints
    return run_wfc(
        width=width,
        height=height,
        sample_type=0,
        periodic_output=periodic_output,
        seed=seed,
        verbose=verbose,
        tiles=tiles,
        neighbors=neighbors,
    )


def generate_map(
    width=9,
    height=9,
    periodic_output=False,
    final_tile_size=1,
    specific_map=None,
    sample_map=None,
    max_height=6,
    N=2,
    periodic_input=False,
    ground=False,
    nb_samples=1,
    symmetry=1,
    verbose=False,
    tiles=None,
    neighbors=None,
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
        max_height: maximum height of the map. For example, max_height=8 means that the map has
            8 different heights.
        N: size of patterns to be used by WFC.
        periodic_input: Whether the input is toric (WFC param).
        ground: Whether to use the lowest middle pattern to initialize the bottom of the map (WFC param).
        nb_samples: Number of samples to generate at once (WFC param).
        symmetry: Levels of symmetry to be used when sampling from a map. Values
            larger than one might imply in new tiles, which might be a unwanted behaviour
            (WFC param).
    """

    # Generate seed for C++
    seed = generate_seed()

    if specific_map is not None:
        img = specific_map

    else:
        img = generate_2d_map(
            width,
            height,
            sample_from=sample_map,
            periodic_output=periodic_output,
            N=N,
            periodic_input=periodic_input,
            ground=ground,
            nb_samples=nb_samples,
            symmetry=symmetry,
            seed=seed,
            verbose=verbose,
            tiles=tiles,
            neighbors=neighbors,
        )

    # Get the dimensions of map - since if plotting a specific_map, we might have different ones
    width = img.shape[0]
    height = img.shape[1]

    img_np = decode_rgb(img, specific_map=specific_map, sample_from=sample_map, max_height=max_height)

    # Let's say we want tiles of final_tile_size x final_tile_size pixels
    # TODO: change variables and make this clearer

    # We create the mesh centered in (0,0)
    x = np.linspace(-height / 2, height / 2, GRANULARITY * height)
    z = np.linspace(-width / 2, width / 2, GRANULARITY * width)

    # Create mesh grid
    x, z = np.meshgrid(x, z)

    # Nowm we create the z coordinates
    # First we split the procedurally generated image into tiles a format (:,:,2,2) in order to
    # do the interpolation and get the z values on our grid
    img_np = np.array(np.hsplit(np.array(np.hsplit(img_np, height)), width))

    # Here, we create the mesh
    # As we are using tiles of two by two, first we have to find a interpolation on
    # the x axis for each tile
    # and then on the y axis for each tile
    # In order to do so, we can use np.linspace, and then transpose the tensor and
    # get the right order
    y = np.linspace(img_np[:, :, :, 0], img_np[:, :, :, 1], GRANULARITY)
    y = np.linspace(y[:, :, :, 0], y[:, :, :, 1], GRANULARITY)
    y = np.transpose(y, (2, 0, 3, 1)).reshape((width * GRANULARITY, height * GRANULARITY), order="A")

    coordinates = np.stack([x, y, z])

    return coordinates, np.array(img)
