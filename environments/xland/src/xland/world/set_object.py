"""
Main functions for setting objects on the map.
"""

from collections import defaultdict, deque

import numpy as np

import simenv as sm

from ..utils import constants, get_connected_components


def get_connectivity_graph(z):
    """
    Returns connectivity graph.

    NOTE: Here we are supposing that every ramp
    is connected from a lower level to a higher level.
    If this is something that might not happen anymore,
    we should change this function.

    TODO: Should we implement this in C++ instead?
    TODO: update this when adding diagonal tiles
    """
    edges = defaultdict(list)
    N, M, _ = z.shape
    nodes = np.arange(N * M).reshape((N, M))

    for x in range(N):
        for y in range(M):

            min_x, max_x, min_y, max_y = max(0, x - 1), min(N, x + 2), max(0, y - 1), min(M, y + 2)

            neighborhood = z[min_x:max_x, min_y:max_y]
            sub_nodes = nodes[min_x:max_x, min_y:max_y]
            non_diagonal_connections = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])[
                min_x - x + 1 : max_x - x + 1, min_y - y + 1 : max_y - y + 1
            ]

            # Going down
            going_down = z[x, y, 0] > neighborhood[:, :, 0]
            going_down = np.logical_and(going_down, non_diagonal_connections)

            # Same level tiles
            same_level = np.logical_and(z[x, y, 0] == neighborhood[:, :, 0], neighborhood[:, :, 1] == 0)
            same_level = np.logical_and(same_level, non_diagonal_connections)

            # Connection with ramp
            neigh_shp = neighborhood.shape
            going_ramp = np.zeros(neigh_shp[:-1], dtype=bool)

            # Going up from a ramp
            going_up = np.zeros(neigh_shp[:-1], dtype=bool)

            # Coordinates of the center
            center_x = int(x != 0)
            center_y = int(y != 0)

            # Now we fill the values considering that we might have corner cases:
            # 1. Taking a ramp down:
            if x < N - 1:
                idx_x = neigh_shp[0] - 1

                # Get if we going to other level
                going_ramp[idx_x, center_y] = np.logical_and(
                    z[x, y, 0] == neighborhood[idx_x, center_y, 0], neighborhood[idx_x, center_y, 1] == 1
                )

                # Get going_up as well from a ramp going down
                going_up[idx_x, center_y] = np.logical_and(
                    z[x, y, 0] + 1 == neighborhood[idx_x, center_y, 0], z[x, y, 1] == 1
                )

            # 2. Going left from a ramp
            if y < M - 1:
                idx_y = neigh_shp[1] - 1
                going_ramp[center_x, idx_y] = np.logical_and(
                    z[x, y, 0] == neighborhood[center_x, idx_y, 0], neighborhood[center_x, idx_y, 1] == 2
                )
                going_up[center_x, idx_y] = np.logical_and(
                    z[x, y, 0] + 1 == neighborhood[center_x, idx_y, 0], z[x, y, 1] == 2
                )

            # 3. Going up from a ramp
            if x > 0:
                going_ramp[0, center_y] = np.logical_and(
                    z[x, y, 0] == neighborhood[0, center_y, 0], neighborhood[0, center_y, 1] == 3
                )
                going_up[0, center_y] = np.logical_and(z[x, y, 0] + 1 == neighborhood[0, center_y, 0], z[x, y, 1] == 3)

            # 4. Going right from a ramp
            if y > 0:
                going_ramp[center_x, 0] = np.logical_and(
                    z[x, y, 0] == neighborhood[center_x, 0, 0], neighborhood[center_x, 0, 1] == 4
                )
                going_up[center_x, 0] = np.logical_and(z[x, y, 0] + 1 == neighborhood[center_x, 0, 0], z[x, y, 1] == 4)

            # Add edges
            edges[y + M * x] = np.concatenate(
                [sub_nodes[going_down], sub_nodes[going_up], sub_nodes[going_ramp], sub_nodes[same_level]]
            )

    return nodes, edges


def get_playable_area(z):
    """
    Returns playable area.

    The algorithm used is dfs to get strongly connected components.
    Then we select the largest strongly connected component to be the "playable area".

    TODO: Getting as input the 1x1 tiles encoded in RGB.
    """

    # Get connectivity graph
    nodes, edges = get_connectivity_graph(z)

    # Get connected components
    n_nodes = nodes.shape[0] * nodes.shape[1]
    connected_components = get_connected_components(n_nodes, edges)

    # Get largest connected component
    component_lens = [len(c) for c in connected_components]
    largest_connected_component = connected_components[np.argmax(component_lens)]
    connected_components_mask = np.zeros(n_nodes, dtype=bool)
    connected_components_mask[largest_connected_component] = True

    # Return indexes of the playable area and if the playable area is larger than
    # the threshold.
    return largest_connected_component, len(largest_connected_component) / n_nodes


def get_mask_connected_components(component, final_shp):
    """
    Returns mask of connected components.
    """
    connected_components_mask = np.zeros(np.prod(final_shp), dtype=bool)
    connected_components_mask[component] = True
    return np.reshape(connected_components_mask, final_shp)


def get_distribution(playable_area, distribution="uniform"):
    """
    Get non-linear distribution of where to place objects.
    """
    if distribution == "uniform":
        int_values = playable_area.astype(float)
        return int_values / np.sum(int_values)

    else:
        raise NotImplementedError


def sample_index(n, p):
    """
    Sample index considering a matrix of probabilities.
    """
    i = np.random.choice(np.arange(p.size), p=p.ravel(), size=n, replace=False)
    return np.unravel_index(i, p.shape)


def create_objects(positions, object_type=None):
    """
    Create objects in simenv.
    """
    if object_type is not None:
        # Generate this type of object
        colors = np.random.choice(COLORS, size=len(positions))

        return [simenv.Cube(position=pos, color=color) for pos, color in zip(positions, colors)]

    else:
        # Choose among options of objects
        # TODO: do this as soon as we see how to deal with colliders
        raise NotImplementedError()


def get_object_pos(z, n_objects, threshold=0.5, distribution="uniform"):
    """
    Returns None if there is not a playable area.
    """
    playable_nodes, area = get_playable_area(z)

    if area < threshold:
        print("Unsufficient playable area: {} when minimum is {}".format(area, threshold))
        return None, False

    # Get probabilities to where to place objects
    # TODO: add option to do the same as it's done in XLand from Deepmind
    probabilities = get_distribution(
        get_mask_connected_components(playable_nodes, final_shp=z.shape[:-1]), distribution=distribution
    )
    obj_pos = sample_index(n_objects, probabilities)

    # Return True showing that object placement was successful
    return obj_pos, True
