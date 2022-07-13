import random
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np


def generate_prims_maze(
    size: Tuple[int, int],
    cell_width: Optional[float] = 1.0,
    xmin: Optional[float] = 0.0,
    ymin: Optional[float] = 0.0,
    keep_prob: Optional[int] = 5,
):
    """
    size: The size of map in the x and yz directions
    cell_width: the cell spacing in metres
    xmin: the minimum x coord of the map
    ymin: the minimum y coord of the map
    keep_prob: the probability - keep_prob/10 if randomly removing a wall for the complete prim's maze

    """
    range_start_x = 0  # (-size //2)
    range_end_x = size[0]  # //2
    range_start_y = 0  # (-size //2)
    range_end_y = size[1]  # //2

    walls = {}
    for i in range(range_start_x, range_end_x):
        for j in range(range_start_y, range_end_y):

            if i != range_end_x - 1 and random.randint(0, 9) < keep_prob:
                # vertical
                start_x = i * cell_width + cell_width + xmin
                end_x = i * cell_width + cell_width + xmin
                start_y = j * cell_width + ymin
                end_y = j * cell_width + cell_width + ymin

                walls[(i, j, i + 1, j)] = (start_x, start_y, end_x, end_y)
            # horizontal
            if j != range_end_x - 1 and random.randint(0, 9) < keep_prob:
                start_x = i * cell_width + xmin
                end_x = i * cell_width + cell_width + xmin
                start_y = j * cell_width + cell_width + ymin
                end_y = j * cell_width + cell_width + ymin

                walls[(i, j, i, j + 1)] = (start_x, start_y, end_x, end_y)

    extents_x = [
        range_start_x * cell_width + xmin,
        range_start_x * cell_width + xmin,
        range_end_x * cell_width + xmin,
        range_end_x * cell_width + xmin,
        range_start_x * cell_width + xmin,
    ]

    extents_y = [
        range_start_y * cell_width + ymin,
        range_end_y * cell_width + ymin,
        range_end_y * cell_width + ymin,
        range_start_y * cell_width + ymin,
        range_start_y * cell_width + ymin,
    ]

    # create the neighbours dict
    neighbours = {}
    for i in range(range_start_x, range_end_x):
        for j in range(range_start_y, range_end_y):
            neighbours[(i, j)] = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]

    def valid_neighbour(i, j):
        return i >= range_start_x and i < range_end_x and j >= range_start_y and j < range_end_y

    def walk(current_i, current_j):
        visited.add((current_i, current_j))
        n = neighbours[(current_i, current_j)]
        random.shuffle(n)
        for (ni, nj) in n:
            if valid_neighbour(ni, nj) and (ni, nj) not in visited:
                if (current_i, current_j, ni, nj) in walls:

                    del walls[(current_i, current_j, ni, nj)]
                if (ni, nj, current_i, current_j) in walls:
                    del walls[(ni, nj, current_i, current_j)]
                walk(ni, nj)

    visited = set()
    start_i = random.randint(range_start_x, range_end_x - 1)
    start_j = random.randint(range_start_y, range_end_y - 1)
    walk(start_i, start_j)

    walls = [w for w in walls.values()]
    exterior_walls = [(x, y) for x, y in zip(extents_x, extents_y)]
    for i in range(4):
        walls.append([*exterior_walls[i], *exterior_walls[i + 1]])

    return walls
