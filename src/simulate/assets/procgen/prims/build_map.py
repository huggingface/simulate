# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
import random
from typing import List, Tuple


def generate_prims_maze(
    size: Tuple[int, int], cell_width: float = 1.0, xmin: float = 0.0, ymin: float = 0.0, keep_prob: int = 5
) -> list:
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

    def valid_neighbour(a: int, b: int) -> bool:
        return range_start_x <= a < range_end_x and range_start_y <= b < range_end_y

    def walk(current_i: int, current_j: int):
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

    walls_list: List = [w for w in walls.values()]
    exterior_walls = [(x, y) for x, y in zip(extents_x, extents_y)]
    for i in range(4):
        walls_list.append([*exterior_walls[i], *exterior_walls[i + 1]])

    return walls_list
