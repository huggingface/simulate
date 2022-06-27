"""
Files used for scene generation.
"""

import numpy as np

import simenv as sm
from simenv.assets.procgen import GRANULARITY, HEIGHT_CONSTANT

from ..utils import convert_to_actual_pos
from .set_agent import create_agents
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


def generate_colliders(sg):
    """
    Generate colliders for mesh.
    """
    width, height, _ = sg.map_2d.shape
    collider_assets = []

    for i in range(width):
        for j in range(height):
            position = [
                -height / 2 + (j + 0.5),
                HEIGHT_CONSTANT * (sg.map_2d[i][j][0] + 0.5) - HEIGHT_CONSTANT,
                -width / 2 + (i + 0.5),
            ]

            angle = np.arctan(HEIGHT_CONSTANT)
            angle_deg = angle * 180 / np.pi
            angles = [0, 0, 0]

            # Calculate the bounding box:
            if sg.map_2d[i][j][1] == 0:
                bounding_box = (1, HEIGHT_CONSTANT, 1)
            else:
                position[1] += (HEIGHT_CONSTANT / 2) * np.cos(angle)

                if sg.map_2d[i][j][1] % 2 == 1:
                    bounding_box = (1, HEIGHT_CONSTANT, 1 / np.cos(angle))

                    ramp_or = -2 * int(sg.map_2d[i][j][1] == 1) + 1
                    position[2] += -ramp_or * (HEIGHT_CONSTANT / 2) * np.sin(angle)

                    # Change angle x since it is a ramp
                    angles[0] = ramp_or * angle_deg

                else:
                    bounding_box = (1 / np.cos(angle), HEIGHT_CONSTANT, 1)

                    ramp_or = -2 * int(sg.map_2d[i][j][1] == 4) + 1
                    position[0] += ramp_or * (HEIGHT_CONSTANT / 2) * np.sin(angle)

                    # Changle angle z since it is a ramp
                    angles[2] = ramp_or * angle_deg

            collider_assets.append(
                sm.Asset(
                    position=position,
                    rotation=sm.utils.quat_from_degrees(*angles),
                    collider=sm.Collider(type=sm.ColliderType.BOX, bounding_box=bounding_box),
                )
            )

    return collider_assets


def generate_scene(sg, obj_pos, agent_pos, engine=None, executable=None, port=None, headless=None, verbose=False):
    """
    Generate scene by interacting with simenv library.
    """
    # Create scene and add camera
    if engine is not None and engine != "pyvista":
        if port is not None:
            scene = sm.Scene(engine=engine, engine_exe=executable, engine_port=port, engine_headless=headless)
        else:
            scene = sm.Scene(engine=engine, engine_exe=executable, engine_headless=headless)

        scene += sm.Camera(position=[0, 10, -5], rotation=[0, 1, 0.50, 0])

    else:
        scene = sm.Scene(engine=engine)

    # Add colliders to StructuredGrid
    sg.generate_3D()
    obj_pos = convert_to_actual_pos(obj_pos, sg.coordinates)
    agent_pos = convert_to_actual_pos(agent_pos, sg.coordinates)

    # Add structured grid, sides and bottom of the map
    x, y, z = sg.coordinates
    scene += sg
    scene += get_sides_and_bottom(x, y, z)

    # Add walls to prevent agent from falling
    scene += add_walls(x, z, height=np.max(y) + 1.5 * HEIGHT_CONSTANT)

    # Add objects
    objects = create_objects(obj_pos)
    scene += objects

    # Add colliders
    sg += generate_colliders(sg)

    # Add agent
    # TODO: Generate random predicates
    scene += create_agents(agent_pos, objects, predicate=None, verbose=verbose)

    return scene
