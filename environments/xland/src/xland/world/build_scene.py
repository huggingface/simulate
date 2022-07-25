"""
Files used for scene generation.
"""

import numpy as np

import simenv as sm

from ..utils import HEIGHT_CONSTANT, convert_to_actual_pos
from .set_agent import create_agents
from .set_object import create_objects
from matplotlib import pyplot as plt
import PIL


# Height of walls and height of box colliders of plane tiles
MAX_SIZE = 10


def add_walls(x, z, height=None, thickness=1):
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
        height = MAX_SIZE * HEIGHT_CONSTANT

    x_min, z_min, x_max, z_max = np.min(x), np.min(z), np.max(x), np.max(z)

    return [
        sm.Asset(
            position=[0, -HEIGHT_CONSTANT, z_max + thickness / 2],
            collider=sm.Collider(
                type=sm.ColliderType.BOX,
                bounding_box=[x_max - x_min, height, thickness],
            ),
        ),
        sm.Asset(
            position=[0, -HEIGHT_CONSTANT, z_min - thickness / 2],
            collider=sm.Collider(
                type=sm.ColliderType.BOX,
                bounding_box=[x_max - x_min, height, thickness],
            ),
        ),
        sm.Asset(
            position=[x_max + thickness / 2, -HEIGHT_CONSTANT, 0],
            collider=sm.Collider(
                type=sm.ColliderType.BOX,
                bounding_box=[thickness, height, z_max - z_min],
            ),
        ),
        sm.Asset(
            position=[x_min - thickness / 2, -HEIGHT_CONSTANT, 0],
            collider=sm.Collider(
                type=sm.ColliderType.BOX,
                bounding_box=[thickness, height, z_max - z_min],
            ),
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
                    collider=sm.Collider(type=sm.ColliderType.BOX, bounding_box=bounding_box),
                )
            )

    return collider_assets


def generate_scene(
    sg,
    obj_pos,
    agent_pos,
    engine=None,
    executable=None,
    port=None,
    headless=None,
    verbose=False,
    root_value=0,
    physics_update_rate=20,
    frame_skip=4,
):
    """
    Generate scene using simenv library.
    """

    # Create root
    this_map = max(root_value, 0)
    root = sm.Asset(name="root_" + str(this_map))

    # Add colliders to StructuredGrid
    material = sm.Material.GRAY25
    sg.generate_3D(material=material)

    from matplotlib.colors import ListedColormap
    import matplotlib.pyplot as plt
    import numpy as np

    import pyvista as pv

    low_point = list(sg.structured_grid.center)
    low_point[1] = sg.structured_grid.bounds[2]
    high_point = list(sg.structured_grid.center)
    high_point[1] = sg.structured_grid.bounds[3]
    elevation = sg.structured_grid.elevation(low_point=low_point, high_point=high_point, scalar_range=(low_point[1],high_point[1]))
    print(elevation['Elevation'])

    # Define the colors we want to use
    blue = np.array([12 / 256, 238 / 256, 246 / 256, 1.0])
    black = np.array([11 / 256, 11 / 256, 11 / 256, 1.0])
    grey = np.array([189 / 256, 189 / 256, 189 / 256, 1.0])
    yellow = np.array([255 / 256, 247 / 256, 0 / 256, 1.0])
    red = np.array([1.0, 0.0, 0.0, 1.0])

    mapping = np.linspace(elevation['Elevation'].min(), elevation['Elevation'].max(), 256)
    newcolors = np.empty((256, 4))
    newcolors[mapping > 2.7001] = black
    newcolors[mapping <= 2.7001] = blue
    newcolors[mapping <= 1.8001] = red
    newcolors[mapping <= 0.9001] = grey
    newcolors[mapping == 0.0] = yellow

    # Make the colormap from the listed colors
    my_colormap = ListedColormap(newcolors)
    img = elevation.plot(scalars='Elevation', cmap=my_colormap, screenshot=True)
    print(len(elevation['Elevation']))
    fig, ax = plt.subplots()
    ax.pcolormesh(np.array(elevation['Elevation']).reshape((80,100), order="F"), cmap=my_colormap, rasterized=True)
    fig.canvas.draw()
    pil_img = PIL.Image.frombytes('RGB', 
        fig.canvas.get_width_height(),fig.canvas.tostring_rgb())
    material = sm.Material(base_color_texture=pil_img)
    a = sm.Box(material=material)
    root += a
    # data = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    # data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    obj_pos = convert_to_actual_pos(obj_pos, sg.coordinates)
    agent_pos = convert_to_actual_pos(agent_pos, sg.coordinates)

    # Add structured grid, sides and bottom of the map
    x, y, z = sg.coordinates

    # Add colliders
    sg += generate_colliders(sg)

    # Add procedurally generated grid and sides and bottom
    map_root = sm.Asset(name="map_root_" + str(this_map))
    map_root += sg
    map_root += get_sides_and_bottom(x, y, z, material=material)

    # Add walls to prevent agent from falling
    map_root += add_walls(x, z)
    root += map_root

    # Add objects
    objects_root = sm.Asset(name="objects_root_" + str(this_map))
    objects = create_objects(obj_pos, n_instance=this_map)
    objects_root += objects
    root += objects_root

    # Add agent
    # TODO: Generate random predicates
    agents_root = sm.Asset(name="agents_root_" + str(this_map))
    agents_root += create_agents(agent_pos, objects, predicate="random", verbose=verbose, n_instance=this_map)
    root += agents_root

    if engine is not None and engine.lower() != "pyvista":
        root += sm.Camera(position=[0, 10, -5], rotation=[0, 1, 0.50, 0])
        root += sm.Light(name="sun_" + str(this_map), position=[0, 20, 0], intensity=0.9)

    if root_value > -1:
        return root

    if engine is not None and engine.lower() != "pyvista":
        if port is not None:
            scene = sm.Scene(
                engine=engine,
                engine_exe=executable,
                engine_port=port,
                engine_headless=headless,
                physics_update_rate=physics_update_rate,
                frame_skip=frame_skip,
            )

        else:
            scene = sm.Scene(
                engine=engine,
                engine_exe=executable,
                engine_headless=headless,
                physics_update_rate=physics_update_rate,
                frame_skip=frame_skip,
            )

    else:
        scene = sm.Scene(engine=engine)

    scene += root

    return scene
