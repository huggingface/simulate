import simenv as sm
import numpy as np

print("First scene")
scene = sm.Scene()

# Create mesh
# First value is the height of the tile
# Second gives information if it's a plain tile or a ramp
# Third doesn't have information associated for now. 
# Ideally the user could create
# their own functions to handle decoding the information.
specific_map = np.array([[[0,0,0], [0,0,0]], [[1,0,0], [1,0,0]], \
    [[1,0,0], [0,0,0]]], dtype=int)
scene += sm.ProcgenGrid(specific_map=specific_map)
scene += sm.Light()
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
# You can use some help functions in wfc_binding: 
# Using tiles:
# TODO: add a python wrapper
tiles = [sm.build_wfc_tile(tile=[[i, 0, 0]], symmetry="X", name="level_" \
    + str(i), weight=1.0 - i * 0.5) for i in range(2)]

# Create constraints that define which tiles can be neighbors
_neighbors = [["level_1", "level_0", 0, 0], ["level_0", "level_0", 0, 0], \
    ["level_1", "level_1", 0, 0]]
neighbors = [sm.build_wfc_neighbor(left=_neighbor[0], right=_neighbor[1], \
    left_or=_neighbor[2], right_or=_neighbor[3]) for _neighbor in _neighbors]

scene += sm.ProcgenGrid(width=5, height=5, tiles=tiles, neighbors=neighbors)

scene.show()
input("Press Enter to close")

scene.close()
