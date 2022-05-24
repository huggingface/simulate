"""
Builds map using Wave Function Collapse.

NOTE: This file is still a draft.
"""

import os
from .gen_tiles import generate_tiles
import numpy as np
import simenv as sm
from PIL import Image
import wfc_binding


def get_back(x, y, z, down, base=0):

    xx_0 = x[0,:]
    yx_0 = [y[0,0]] * 2
    xx_0, yx_0 = np.meshgrid(xx_0, yx_0)
    zx_0 = np.zeros(xx_0.shape)
    zx_0[0, :] = z[0,:]
    zx_0[1, :] = down

    xx_1 = x[-1,:]
    yx_1 = [y[-1,0]] * 2
    xx_1, yx_1 = np.meshgrid(xx_1, yx_1)
    zx_1 = np.zeros(xx_1.shape)
    zx_1[0, :] = z[-1,:]
    zx_1[1, :] = down
    
    yy_0 = y[:,0]
    xy_0 = [x[0,0]] * 2
    xy_0, yy_0 = np.meshgrid(xy_0, yy_0)
    zy_0 = np.zeros(xy_0.shape)
    zy_0[:, 0] = z[:,0]
    zy_0[:, 1] = down

    yy_1 = y[:,-1]
    xy_1 = [x[0,-1]] * 2
    xy_1, yy_1 = np.meshgrid(xy_1, yy_1)
    zy_1 = np.zeros(xy_1.shape)
    zy_1[:, 0] = z[:,-1]
    zy_1[:, 1] = down

    structures = [
        sm.StructuredGrid(x=x, y=y, z=np.full(x.shape, down)),
        sm.StructuredGrid(x=xx_0, y=yx_0, z=zx_0),
        sm.StructuredGrid(x=xx_1, y=yx_1, z=zx_1),
        sm.StructuredGrid(x=xy_0, y=yy_0, z=zy_0),
        sm.StructuredGrid(x=xy_1, y=yy_1, z=zy_1),

    ]

    return structures[0] + structures[1] + structures[2] + structures[3] + structures[4]


def generate_2d_map(seed, width, height, gen_folder, periodic_output=False):
    """
    TODO: implement this function to have a binding with c++
    """
    # TODO: Open image if it's cached

    # Otherwise, generate it:
    wfc_binding.py_main(width, height, periodic_output)
    img_path = os.path.join(gen_folder, 'maps/tiles.png')

    # Read file
    img = Image.open(img_path) 
    return img


def generate_map(seed, 
                width, 
                height, 
                periodic_output=False,
                tile_size=10, 
                gen_folder=".gen_files",
                or_tile_size=2,
                height_constant=0.2,
                specific_map=None):
    """
    Generate the map.

    Args:
        seed: The seed to use for the generation of the map.
        width: The width of the map.
        height: The height of the map.
        tile_size: The size of the resulting tiles.
        gen_folder: where to find all generation-necessary files.
        or_tile_size: The size of the tiles in the original image.

    NOTE: This is a draft.
    """

    if specific_map is None:
        img = generate_2d_map(seed, width, height, gen_folder)
    else:
        img = Image.open(os.path.join(gen_folder, "maps", specific_map))
        width = img.width // or_tile_size
        height = img.height // or_tile_size

    img_np = np.array(img)
    img_np = img_np[:,:,0] * height_constant

    # First we will just extract the map and plot
    z_grid = img_np 

    # Let's say we want tiles of tile_size x tile_size pixels, and a certain "size" on number
    # of tiles:
    # TODO: change variables and make this clearer
    # Number of divisions for each tile on the mesh
    granularity = 10

    x = np.arange(- width * tile_size // 2, width * tile_size // 2, tile_size / granularity)
    y = np.arange(- height * tile_size // 2, height * tile_size // 2, tile_size / granularity)

    x, y = np.meshgrid(x, y)

    # create z_grid
    img_np = np.array(np.hsplit(np.array(np.hsplit(img_np, width)), height))

    z_grid = np.linspace(img_np[:,:,:,0], img_np[:,:,:,1], granularity)
    z_grid = np.linspace(z_grid[:,:,:,0], z_grid[:,:,:,1], granularity)
    z_grid = np.transpose(z_grid, (2, 0, 3, 1)).reshape((height * granularity, width * granularity), order='A')

    scene = sm.Scene()
    scene += sm.StructuredGrid(x=x, y=y, z=z_grid)
    scene += get_back(x, y, z_grid, down=-10)

    # scene += sm.Rectangle(points=
    #                         [[min_x, min_y, ]])
    # scene += sm.StructuredGrid(x=np.full(np.min(x), x.shape), y=y, z=np.full(x.shape, -10))

    
    print(scene)
    scene.show(in_background=False)
    # scene.engine.show(interactive=True, auto_close=False, interactive_update=True, screenshow=True)

    

