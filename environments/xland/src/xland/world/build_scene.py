"""
Files used for scene generation.
"""

from ..utils import HEIGHT_CONSTANT
from .set_object import create_objects
import numpy as np
import simenv as sm


def add_walls(x, y, height=None, thickness=0.1):
    """
    Adding walls to prevent agent from falling.

    Args:
        x: x coordinates in grid
        y: y coordinates in grid
        height: height of walls
        thickness: thickness of walls
    
    Returns:
        List of cubes that correspond to walls to prevent
            agent of falling
    """
    if height is None:
        height = 10 * HEIGHT_CONSTANT

    x_min, y_min, x_max, y_max = np.min(x), np.min(y), np.max(x), np.max(y)
    # Add transparent material:
    material = sm.Material(base_color=(0.9, 0.8, 0.2, 0.1))

    return [
        sm.Cube(position=[0, -HEIGHT_CONSTANT, y_max], 
            bounds=[x_min, x_max, 0, height, 0, thickness], material=material),
        sm.Cube(position=[0, -HEIGHT_CONSTANT, y_min], 
            bounds=[x_min, x_max, 0, height, 0, -thickness], material=material),
        sm.Cube(position=[x_max, -HEIGHT_CONSTANT, 0], 
            bounds=[0, thickness, 0, height, y_min, y_max], material=material),
        sm.Cube(position=[x_min, -HEIGHT_CONSTANT, 0], 
            bounds=[0, -thickness, 0, height, y_min, y_max], material=material),
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
    yx_0 = [y[0, 0]] * 2
    xx_0, yx_0 = np.meshgrid(xx_0, yx_0)
    zx_0 = np.zeros(xx_0.shape)
    zx_0[0, :] = -HEIGHT_CONSTANT
    zx_0[1, :] = z[0, :]

    xx_1 = x[-1, :]
    yx_1 = [y[-1, 0]] * 2
    xx_1, yx_1 = np.meshgrid(xx_1, yx_1)
    zx_1 = np.zeros(xx_1.shape)
    zx_1[0, :] = z[-1, :]
    zx_1[1, :] = -HEIGHT_CONSTANT

    yy_0 = y[:, 0]
    xy_0 = [x[0, 0]] * 2
    xy_0, yy_0 = np.meshgrid(xy_0, yy_0)
    zy_0 = np.zeros(xy_0.shape)
    zy_0[:, 0] = -HEIGHT_CONSTANT
    zy_0[:, 1] = z[:, 0]

    yy_1 = y[:, -1]
    xy_1 = [x[0, -1]] * 2
    xy_1, yy_1 = np.meshgrid(xy_1, yy_1)
    zy_1 = np.zeros(xy_1.shape)
    zy_1[:, 0] = z[:, -1]
    zy_1[:, 1] = -HEIGHT_CONSTANT

    # Down base
    x_down = [x[0, -1], x[0, 0]]
    y_down = [y[0, 0], y[-1, 0]]
    x_down, y_down = np.meshgrid(x_down, y_down)
    z_down = np.full(x_down.shape, -HEIGHT_CONSTANT)

    # We get each of the extra structures
    # We use z as y since it's the way it is in most game engines:
    structures = [
        sm.StructuredGrid(x=x_down, y=z_down, z=y_down, name="bottom_surface"),
        sm.StructuredGrid(x=xx_0, y=zx_0, z=yx_0),
        sm.StructuredGrid(x=xx_1, y=zx_1, z=yx_1),
        sm.StructuredGrid(x=xy_0, y=zy_0, z=yy_0),
        sm.StructuredGrid(x=xy_1, y=zy_1, z=yy_1),
    ]

    return structures

def generate_scene(generated_map, obj_pos, engine=None):
    """
    Generate scene by interacting with simenv library.
    """
    # Create the mesh
    x, y, z = generated_map
    scene = sm.Scene(engine=engine)

    # We use z as y since it's the way it is in most game engines:
    scene += sm.StructuredGrid(x=x, y=z, z=y, name="top_surface")
    scene += get_sides_and_bottom(x, y, z)
    scene += add_walls(x, y)
    
    # Add objects
    scene += create_objects(obj_pos)

    # Add camera
    if engine is not None:
        scene += sm.Camera(position=[0, 5, -10], rotation=[0, 1, 0.25, 0])
    
    # Add agent
    # TODO
    
    return scene