# Pregenerated maps

The folder examples contains some example maps that can be built, in order to be used by the Wave Function Collapse to procedurally generate more maps.

So far, maps are saved as npy files.

Each map is a 2D combination of tiles, and each tile is a height map of NxM dimensions. Therefore, the maps that are stored have dimensions of PxQxNxM, where P and Q are the width and height of the map respectively. 

Example: a ramp can be expressed as a tile of the following format:`[[0, 0], [1, 1]]`. On the other hand, a plain tile of height 0 can be expressed as `[[0, 0], [0, 0]]`.