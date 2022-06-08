# Pregenerated maps

The folder examples contains txt files with maps that can be built, in order to be used by the Wave Function Collapse to procedurally generate more maps.

So far, maps are saved as csv files, to improve readability by users.

Each tile is encoded by two numbers: 

1. The first one corresponds to the height of the tile.

2. The second one corresponds to the tile type (where ramps go from lower to higher level):

    0: plain tile.

    1: ramp from top to bottom.
    
    2: ramp from left to right.
    
    3: ramp from bottom to top.
    
    4: ramp from right to left.