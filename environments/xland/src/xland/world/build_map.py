"""
Files used for scene generation.
"""

import numpy as np

import simulate as sm

from ..utils import HEIGHT_CONSTANT, convert_to_actual_pos
from .set_agent import create_agents
from .set_object import create_objects


# Height of walls and height of box colliders of plane tiles
MAX_SIZE = 10


def add_walls(x, z, height=None, thickness=0.5, invisible=False):
    """
    Adding walls to prevent agent from falling.

    Args:
        x: x coordinates in grid
        z: z coordinates in grid
        height: height of walls
        thickness: thickness of walls
        invisible: if walls should be invisible

    Returns:
        List of cubes that correspond to walls to prevent
            agent of falling
    """
    if height is None:
        height = MAX_SIZE * HEIGHT_CONSTANT

    x_min, z_min, x_max, z_max = np.min(x), np.min(z), np.max(x), np.max(z)

    if invisible:
        return [
            sm.Asset(
                position=[0, -HEIGHT_CONSTANT, z_max + thickness / 2],
                collider=sm.Collider(
                    type="box",
                    bounding_box=[x_max - x_min, height, thickness],
                ),
            ),
            sm.Asset(
                position=[0, -HEIGHT_CONSTANT, z_min - thickness / 2],
                collider=sm.Collider(
                    type="box",
                    bounding_box=[x_max - x_min, height, thickness],
                ),
            ),
            sm.Asset(
                position=[x_max + thickness / 2, -HEIGHT_CONSTANT, 0],
                collider=sm.Collider(
                    type="box",
                    bounding_box=[thickness, height, z_max - z_min],
                ),
            ),
            sm.Asset(
                position=[x_min - thickness / 2, -HEIGHT_CONSTANT, 0],
                collider=sm.Collider(
                    type="box",
                    bounding_box=[thickness, height, z_max - z_min],
                ),
            ),
        ]
    else:
        material = sm.Material.BLACK
        return [
            sm.Box(
                position=[0, -HEIGHT_CONSTANT, z_max + thickness / 2],
                bounds=(x_min - thickness, x_max + thickness, -height / 2, height / 2, -thickness / 2, thickness / 2),
                material=material,
            ),
            sm.Box(
                position=[0, -HEIGHT_CONSTANT, z_min - thickness / 2],
                bounds=(x_min - thickness, x_max + thickness, -height / 2, height / 2, -thickness / 2, thickness / 2),
                material=material,
            ),
            sm.Box(
                position=[x_max + thickness / 2, -HEIGHT_CONSTANT, 0],
                bounds=(-thickness / 2, thickness / 2, -height / 2, height / 2, z_min - thickness, z_max + thickness),
                material=material,
            ),
            sm.Box(
                position=[x_min - thickness / 2, -HEIGHT_CONSTANT, 0],
                bounds=(-thickness / 2, thickness / 2, -height / 2, height / 2, z_min - thickness, z_max + thickness),
                material=material,
            ),
        ]


def get_sides_and_bottom(x, y, z, material):
    """
    Get a bottom basis for the structured grid.

    The main goal of this function is to avoid having a surface
    floating. So, we add a ground a side meshs.

    Args:
        x: x coordinates
        y: y coordinates
        z: z coordinates
        material: material to use on the sides and bottom
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
        sm.StructuredGrid(x=x_down, y=y_down, z=z_down, material=material),
        sm.StructuredGrid(x=xx_0, y=yx_0, z=zx_0, material=material),
        sm.StructuredGrid(x=xx_1, y=yx_1, z=zx_1, material=material),
        sm.StructuredGrid(x=xz_0, y=yz_0, z=zz_0, material=material),
        sm.StructuredGrid(x=xz_1, y=yz_1, z=zz_1, material=material),
    ]

    return structures


def generate_colliders(sg):
    """
    Generate colliders for mesh.
    """
    width, height, _, _ = sg.map_2d.shape
    collider_assets = []

    for i in range(width):
        for j in range(height):

            h = np.min(sg.map_2d[i][j])

            position = [
                -height / 2 + (j + 0.5),
                h + 0.5 - HEIGHT_CONSTANT,
                -width / 2 + (i + 0.5),
            ]

            angle = np.arctan(HEIGHT_CONSTANT)
            angle_deg = angle * 180 / np.pi
            angles = [0, 0, 0]

            # Calculate the bounding box:
            if np.all(sg.map_2d[i][j] == h):
                # We create a large bounding_box to avoid agents falling
                # below ramps
                bounding_box = (1, MAX_SIZE * HEIGHT_CONSTANT, 1)
                position[1] -= ((MAX_SIZE - 1) / 2) * HEIGHT_CONSTANT
            else:
                position[1] += (HEIGHT_CONSTANT / 2) * np.cos(angle)

                if np.all(sg.map_2d[i, j, :, 0] == sg.map_2d[i, j, :, 1]):
                    bounding_box = (1, HEIGHT_CONSTANT, 1 / np.cos(angle))

                    ramp_orientation = -2 * int(sg.map_2d[i, j, 0, 0] < sg.map_2d[i, j, 1, 0]) + 1
                    position[2] += -ramp_orientation * (HEIGHT_CONSTANT / 2) * np.sin(angle)

                    # Change angle x since it is a ramp
                    angles[0] = ramp_orientation * angle_deg

                else:
                    bounding_box = (1 / np.cos(angle), HEIGHT_CONSTANT, 1)

                    ramp_orientation = -2 * int(sg.map_2d[i, j, 0, 0] > sg.map_2d[i, j, 0, 1]) + 1
                    position[0] += ramp_orientation * (HEIGHT_CONSTANT / 2) * np.sin(angle)

                    # Changle angle z since it is a ramp
                    angles[2] = ramp_orientation * angle_deg

            collider_assets.append(
                sm.Asset(
                    position=position,
                    rotation=sm.utils.rotation_from_euler_degrees(*angles),
                    collider=sm.Collider(type="box", bounding_box=bounding_box),
                )
            )

    return collider_assets


def generate_map(
    sg,
    obj_pos,
    agent_pos,
    rank,
    predicate="random",
    camera_width=96,
    camera_height=72,
    object_type=None,
    specific_color=None,
    n_options=1,
    n_conjunctions=2,
    predicates_verbose=True,
    frame_skip=None,
):
    """
    Generate scene using simulate library.
    """

    # Create root
    root = sm.Asset(name=f"root_{rank}")

    # Add colliders to StructuredGrid
    material = sm.Material.GRAY25
    sg.generate_3D(material=material)

    obj_pos = convert_to_actual_pos(obj_pos, sg.coordinates)
    agent_pos = convert_to_actual_pos(agent_pos, sg.coordinates)

    # Add structured grid, sides and bottom of the map
    x, y, z = sg.coordinates

    # Add colliders
    sg += generate_colliders(sg)

    # Add procedurally generated grid and sides and bottom
    map_root = sm.Asset(name=f"map_root_{rank}")
    map_root += sg
    map_root += get_sides_and_bottom(x, y, z, material=material)

    # Add walls to prevent agent from falling
    map_root += add_walls(x, z)
    root += map_root

    # Add objects
    objects_root = sm.Asset(name=f"objects_root_{rank}")
    objects = create_objects(obj_pos, rank=rank, object_type=object_type, specific_color=specific_color)

    objects_root += objects
    root += objects_root

    # Add agent
    # TODO: Generate random predicates
    agents_root = sm.Asset(name=f"agents_root_{rank}")
    agents_root += create_agents(
        agent_pos,
        objects,
        camera_width=camera_width,
        camera_height=camera_height,
        predicate=predicate,
        rank=rank,
        n_options=n_options,
        n_conjunctions=n_conjunctions,
        verbose=predicates_verbose,
        frame_skip=frame_skip,
    )
    root += agents_root

    return root
