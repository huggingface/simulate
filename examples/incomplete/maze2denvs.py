import numpy as np


WALL = 10
EMPTY = 11
GOAL = 12


def parse_maze(maze_str):
    lines = maze_str.strip().split("\\")
    width, height = len(lines), len(lines[0])
    maze_arr = np.zeros((width, height), dtype=np.int32)
    for w in range(width):
        for h in range(height):
            tile = lines[w][h]
            if tile == "#":
                maze_arr[w][h] = WALL
            elif tile == "G":
                maze_arr[w][h] = GOAL
            elif tile == " " or tile == "O" or tile == "0":
                maze_arr[w][h] = EMPTY
            else:
                raise ValueError("Unknown tile type: %s" % tile)
    return maze_arr


LARGE_MAZE = (
    "############\\"
    + "#OOOO#OOOOO#\\"
    + "#O##O#O#O#O#\\"
    + "#OOOOOO#OOO#\\"
    + "#O####O###O#\\"
    + "#OO#O#OOOOO#\\"
    + "##O#O#O#O###\\"
    + "#OO#OOO#OGO#\\"
    + "############"
)

LARGE_MAZE_EVAL = (
    "############\\"
    + "#OO#OOO#OGO#\\"
    + "##O###O#O#O#\\"
    + "#OO#O#OOOOO#\\"
    + "#O##O#OO##O#\\"
    + "#OOOOOO#OOO#\\"
    + "#O##O#O#O###\\"
    + "#OOOO#OOOOO#\\"
    + "############"
)

MEDIUM_MAZE = (
    "########\\" + "#OO##OO#\\" + "#OO#OOO#\\" + "##OOO###\\" + "#OO#OOO#\\" + "#O#OO#O#\\" + "#OOO#OG#\\" + "########"
)

MEDIUM_MAZE_EVAL = (
    "########\\" + "#OOOOOG#\\" + "#O#O##O#\\" + "#OOOO#O#\\" + "###OO###\\" + "#OOOOOO#\\" + "#OO##OO#\\" + "########"
)

SMALL_MAZE = "######\\" + "#OOOO#\\" + "#O##O#\\" + "#OOOO#\\" + "######"

U_MAZE = "#####\\" + "#GOO#\\" + "###O#\\" + "#OOO#\\" + "#####"

U_MAZE_EVAL = "#####\\" + "#OOG#\\" + "#O###\\" + "#OOO#\\" + "#####"

OPEN = "#######\\" + "#OOOOO#\\" + "#OOGOO#\\" + "#OOOOO#\\" + "#######"
