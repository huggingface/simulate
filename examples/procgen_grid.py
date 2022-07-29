import numpy as np

import simenv as sm
from simenv.assets.procgen.wfc import build_wfc_neighbor, build_wfc_tile


print("First scene")
scene = sm.Scene()

# Create mesh
# Height map and, in the future, a map of simenv objects
specific_map = (
    np.array(
        [
            [[[1, 1], [1, 1]], [[1, 1], [1, 1]]],
            [[[1, 1], [0, 0]], [[1, 1], [1, 1]]],
            [[[0, 0], [0, 0]], [[0, 0], [0, 0]]],
        ]
    )
    * 0.6
)
proc_grid = sm.ProcgenGrid(specific_map=specific_map)

# Let's color our grid by height.
# We assign a simple 1D texture to the object and assing mesh texture coordinates from the height of each points of the mesh.
proc_grid.material.base_color_texture = sm.TEXTURE_1D_CMAP  # Set a simple 1D color map texture
height = proc_grid.mesh.points[:, 1, None]  # We get the height coordinates of the mesh points ( theY axis)
texture_coord = np.concatenate(
    [height, np.zeros_like(height)], axis=1
)  # Make texture coordinates (UV) by adding a zeros axis
proc_grid.mesh.active_t_coords = texture_coord  # Assign as point to texture mapping

scene += proc_grid
scene += sm.LightSun()
scene.show()

input("Press Enter for second scene")
scene.close()
scene.clear()

# Second scene: generating from this map
scene += sm.ProcgenGrid(width=3, height=3, sample_map=specific_map)
scene += sm.Light()
scene.show()

input("Press Enter for third scene")
scene.close()
scene.clear()

# Ideally, instead of "hardcoding" the tiles, you would create a function
# to generate them
tiles = 0.6 * np.array([[[i, i], [i, i]] for i in range(2)])

# Weights and symmetries are facultative
weights = [1.0 - i * 0.5 for i in range(2)]
symmetries = ["X"] * 2

# Create constraints that define which tiles can be neighbors
neighbors = [(tiles[1], tiles[0]), (tiles[0], tiles[0]), (tiles[1], tiles[1])]
scene += sm.ProcgenGrid(width=3, height=3, tiles=tiles, neighbors=neighbors, weights=weights, symmetries=symmetries)
scene += sm.Light()

scene.show()
input("Press Enter to close")

scene.close()
