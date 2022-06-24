"""
Files used for scene generation.
"""

import numpy as np

import simenv as sm
from simenv.assets.procgen import HEIGHT_CONSTANT

from .set_object import create_objects


def add_walls(x, z, height=None, thickness=0.1):
    """
    Adding walls to prevent agent from falling.

    Args:
        x: x coordinates in grid
        z: z coordinates in grid
        height: height of walls
        thickness: thickness of walls

    Returns:
        List of cubes that correspond to walls to prevent
            agent of falling
    """
    if height is None:
        height = 10 * HEIGHT_CONSTANT

    x_min, z_min, x_max, z_max = np.min(x), np.min(z), np.max(x), np.max(z)
    # Add transparent material:
    material = sm.Material(base_color=(0.9, 0.8, 0.2, 0.1))

    return [
        sm.Box(
            position=[0, -HEIGHT_CONSTANT, z_max], bounds=[x_min, x_max, 0, height, 0, thickness], material=material
        ),
        sm.Box(
            position=[0, -HEIGHT_CONSTANT, z_min], bounds=[x_min, x_max, 0, height, 0, -thickness], material=material
        ),
        sm.Box(
            position=[x_max, -HEIGHT_CONSTANT, 0], bounds=[0, thickness, 0, height, z_min, z_max], material=material
        ),
        sm.Box(
            position=[x_min, -HEIGHT_CONSTANT, 0], bounds=[0, -thickness, 0, height, z_min, z_max], material=material
        ),
    ]


def get_sides_and_bottom(x, y, z):
    """
    Get a bottom basis for the structured grid.

    The main goal of this function is to avoid having a surface
    floating. So, we add a ground a side meshs.

    Args:
        x: x coordinates
        y: y coordinates
        z: z coordinates
    """
    # TODO: generate 3d mesh with all of this
    # TODO: all of this is being done by hand. Ideally, we want a function
    # that handles all the cases without writing too much code.
    # We calculate the coordinates for each of the sides:
    # Add bottom at first
    xx_0 = x[0, :]
    zx_0 = [z[0, 0]] * 2
    xx_0, zx_0 = np.meshgrid(xx_0, zx_0)
    yx_0 = np.zeros(xx_0.shape)
    yx_0[0, :] = -HEIGHT_CONSTANT
    yx_0[1, :] = y[0, :]

    xx_1 = x[-1, :]
    zx_1 = [z[-1, 0]] * 2
    xx_1, zx_1 = np.meshgrid(xx_1, zx_1)
    yx_1 = np.zeros(xx_1.shape)
    yx_1[0, :] = y[-1, :]
    yx_1[1, :] = -HEIGHT_CONSTANT

    zz_0 = z[:, 0]
    xz_0 = [x[0, 0]] * 2
    xz_0, zz_0 = np.meshgrid(xz_0, zz_0)
    yz_0 = np.zeros(xz_0.shape)
    yz_0[:, 0] = -HEIGHT_CONSTANT
    yz_0[:, 1] = y[:, 0]

    zz_1 = z[:, -1]
    xz_1 = [x[0, -1]] * 2
    xz_1, zz_1 = np.meshgrid(xz_1, zz_1)
    yz_1 = np.zeros(xz_1.shape)
    yz_1[:, 0] = y[:, -1]
    yz_1[:, 1] = -HEIGHT_CONSTANT

    # Down base
    x_down = [x[0, -1], x[0, 0]]
    z_down = [z[0, 0], z[-1, 0]]
    x_down, z_down = np.meshgrid(x_down, z_down)
    y_down = np.full(x_down.shape, -HEIGHT_CONSTANT)

    # We get each of the extra structures
    # We use z as y since it's the way it is in most game engines:
    structures = [
        sm.StructuredGrid(x=x_down, y=y_down, z=z_down, name="bottom_surface"),
        sm.StructuredGrid(x=xx_0, y=yx_0, z=zx_0),
        sm.StructuredGrid(x=xx_1, y=yx_1, z=zx_1),
        sm.StructuredGrid(x=xz_0, y=yz_0, z=zz_0),
        sm.StructuredGrid(x=xz_1, y=yz_1, z=zz_1),
    ]

    return structures


def generate_scene(sg, obj_pos, engine=None):
    """
    Generate scene by interacting with simenv library.
    """
    # Create the mesh
    x, y, z = sg.coordinates
    scene = sm.Scene(engine=engine)

    # Add structured grid, sides and bottom of the map
    scene += sg
    scene += get_sides_and_bottom(x, y, z)

    # Add walls to prevent agent from falling
    scene += add_walls(x, z)

    # Add objects
    scene += create_objects(obj_pos)

    # Add camera
    if engine is not None:
        scene += sm.Camera(position=[0, 5, -10], rotation=[0, 1, 0.25, 0])

    # Add agent
    # TODO

    return scene
