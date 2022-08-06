import numpy as np

import simenv as sm


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

# Example using a predefined colormap from matplotlib
# See https://matplotlib.org/stable/api/cm_api.html#matplotlib.cm.get_cmap
proc_grid.add_texture_cmap_along_axis(axis="y", cmap="viridis", n_colors=5)
scene += proc_grid

scene += sm.LightSun()
scene.show(show_edges=True)

input("Press Enter for second scene")
scene.close()
scene.clear()

# Second scene: generating from this map
scene += sm.ProcgenGrid(width=3, height=3, sample_map=specific_map)

# Example creating our own colormap
# https://matplotlib.org/stable/tutorials/colors/colormap-manipulation.html
from matplotlib.colors import ListedColormap


cmap = ListedColormap(["red", "blue", "green"])
scene.tree_children[0].add_texture_cmap_along_axis(axis="x", cmap=cmap)

scene += sm.LightSun()
scene.show()

input("Press Enter for third scene")
scene.close()
scene.clear()

# Ideally, instead of "hardcoding" the tiles, you would create a function
# to generate them
tiles = 0.6 * np.array([[[i, i, i], [i, i, i], [i, i, i]] for i in range(2)])

# Weights and symmetries are facultative
weights = [1.0 - i * 0.5 for i in range(2)]
symmetries = ["X"] * 2

# Create constraints that define which tiles can be neighbors
neighbors = [(tiles[1], tiles[0]), (tiles[0], tiles[0]), (tiles[1], tiles[1])]
scene += sm.ProcgenGrid(width=3, height=3, tiles=tiles, neighbors=neighbors, weights=weights, symmetries=symmetries)
scene += sm.LightSun()
scene.tree_children[0].add_texture_cmap_along_axis(axis="x", cmap="viridis")

scene.show()
input("Press Enter to close")

scene.close()
