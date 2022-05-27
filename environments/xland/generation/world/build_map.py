"""
Builds map using Wave Function Collapse.

NOTE: This file is still a draft.
"""

import os
from .gen_tiles import generate_tiles
import numpy as np
import simenv as sm
from PIL import Image
from wfc_binding import run_wfc


def get_back(x, y, z, down, base=0):
    """
    Get a base for the structured grid.
    """
    # TODO: reduce code necessary to do this

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

    # Down base
    x_down = [x[0,0], x[0,-1]]
    y_down = [y[0,0], y[-1,0]]
    x_down, y_down = np.meshgrid(x_down, y_down)
    z_down = np.full(x_down.shape, down)

    structures = [
        sm.StructuredGrid(x=x_down, y=y_down, z=z_down),
        sm.StructuredGrid(x=xx_0, y=yx_0, z=zx_0),
        sm.StructuredGrid(x=xx_1, y=yx_1, z=zx_1),
        sm.StructuredGrid(x=xy_0, y=yy_0, z=zy_0),
        sm.StructuredGrid(x=xy_1, y=yy_1, z=zy_1),
    ]

    # TODO: in the structure of the scene, structures 1, 2, 3 and 4 become children of 0, 
    # which is not what we want
    return structures[0] + structures[1] + structures[2] + structures[3] + structures[4]


def decode_rgb(img, height_constant, sample_from=None, max_height=8):
    
    img_np = np.array(img)
    
    if sample_from is None:
        map_2d = img_np[:,:,0] * height_constant
    else:
        height_level = None
        # Create the map
        map_2d = np.zeros((2 * img_np.shape[0], 2 * img_np.shape[1]))

        # TODO: optimize this decoding
        for i in range(img_np.shape[0]):
            for j in range(img_np.shape[1]):
                if img_np[i,j,1] == 0:
                    map_2d[2*i: 2*(i+1), 2*j:2*(j+1)] = img_np[i,j,0]
                elif img_np[i,j,1] == 1:
                    map_2d[2*i, 2*j:2*(j+1)] = img_np[i,j,0]
                    map_2d[2*i+1, 2*j:2*(j+1)] = img_np[i,j,0] + 1
                elif img_np[i,j,1] == 2:
                    map_2d[2*i: 2*(i+1), 2*j] = img_np[i,j,0]
                    map_2d[2*i: 2*(i+1), 2*j+1] = img_np[i,j,0]+1
                elif img_np[i,j,1] == 3:
                    map_2d[2*i, 2*j:2*(j+1)] = img_np[i,j,0] + 1
                    map_2d[2*i+1, 2*j:2*(j+1)] = img_np[i,j,0]
                elif img_np[i,j,1] == 4:
                    map_2d[2*i: 2*(i+1), 2*j] = img_np[i,j,0] + 1
                    map_2d[2*i: 2*(i+1), 2*j+1] = img_np[i,j,0]
        
        map_2d = map_2d * (255. * height_constant * 1 / max_height)

    return map_2d


def generate_2d_map(width, height, gen_folder, periodic_output=True, N=2,
                    periodic_input=False, ground=False, nb_samples=1, 
                    symmetry=1, sample_from=None, seed=None):
    """
    Generate 2d map.
    """
    # TODO: Open image if it's cached

    # Check if seed should be used
    if seed is not None:
        use_seed = True
    else:
        use_seed = False
        seed = 0

    # Otherwise, generate it
    # TODO: fix names, pass name of the file to the c++ function
    if sample_from is not None:
        # overlapping
        run_wfc(width, height, 1, periodic_output=periodic_output,
                N=N, periodic_input=periodic_input, ground=ground, 
                nb_samples=nb_samples, symmetry=symmetry, use_seed=use_seed, 
                seed=seed)
        img_path = os.path.join(gen_folder, 'maps/sampled_image0.png')
    
    else:    
        # simpletiled
        run_wfc(width, height, 0, periodic_output=periodic_output, use_seed=use_seed, seed=seed)
        img_path = os.path.join(gen_folder, 'maps/tiles.png')

    # Read file
    img = Image.open(img_path) 
    return img


def generate_map(width, 
                height, 
                periodic_output=False,
                tile_size=10, 
                gen_folder=".gen_files",
                or_tile_size=2,
                height_constant=0.2,
                specific_map=None,
                sample_from=None,
                max_height=8,
                N=2,
                periodic_input=False, 
                ground=False, 
                nb_samples=1, 
                symmetry=1,
                seed=None):
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

    if specific_map is not None:
        # TODO: deal with images with tiles 2x2
        img = Image.open(os.path.join(gen_folder, "maps", specific_map))
        width = img.width
        height = img.height
    else:
        img = generate_2d_map(width, height, gen_folder, sample_from=sample_from, periodic_output=periodic_output,
                                N=N, periodic_input=periodic_input, ground=ground, nb_samples=nb_samples, symmetry=symmetry,
                                seed=seed)

    img_np = decode_rgb(img, height_constant, sample_from=sample_from, max_height=max_height)
    map_2d = img_np.copy()

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

    scene = sm.Scene() # engine="Unity"
    scene += sm.StructuredGrid(x=x, y=y, z=z_grid)
    scene += get_back(x, y, z_grid, down=-10)

    return (x,y,z_grid), map_2d, scene

    

