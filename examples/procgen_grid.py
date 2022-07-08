import simenv as sm
from simenv.assets.procgen.wfc import build_wfc_neighbor, build_wfc_tile
import numpy as np

print("First scene")
scene = sm.Scene()

# Create mesh
# Height map and, in the future, a map of simenv objects
specific_map = np.array(
    [[[[1,1], [1,1]], [[1,1], [1,1]]], 
    [[[1,1], [0,0]], [[1,1], [1,1]]], \
    [[[0,0], [0,0]], [[0,0], [0,0]]]]) * 0.6
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
