"""
Main functions for setting objects on the map.
"""

from collections import defaultdict

import numpy as np

import simenv as sm

from ..utils import COLOR_NAMES, COLORS, OBJECTS, get_bounds, get_connected_components


def get_connectivity_graph(y):
    """
    Returns connectivity graph.

    NOTE: Here we are supposing that every ramp
    is connected from a lower level to a higher level.
    If this is something that might not happen anymore,
    we should change this function.

    TODO: Should we implement this in C++ instead? or at least vectorize it
    TODO: update this when adding diagonal tiles
    """
    edges = defaultdict(list)
    N, M, _, _ = y.shape
    nodes = np.arange(N * M).reshape((N, M))
    lowest_plain_nodes = []
    min_height = np.min(np.amax(y, axis=(2, 3)))

    # Identify plain tiles to use them to place objects
    plain_tiles = []

    for x in range(N):
        for z in range(M):

            if np.all(y[x, z] == y[x, z, 0, 0]):
                plain_tiles.append(z + M * x)
                # We check if the plain tile is in the lowest height
                # BUG: there is a bug on the connected components that needs to be solved.
                if y[x, z, 0, 0] == min_height:
                    lowest_plain_nodes.append(z + M * x)

            min_x, max_x, min_z, max_z = max(0, x - 1), min(N, x + 2), max(0, z - 1), min(M, z + 2)

            neighborhood = y[min_x:max_x, min_z:max_z]
            sub_nodes = nodes[min_x:max_x, min_z:max_z]

            # Declaration of arrays:
            neigh_shp = neighborhood.shape

            # Coordinates of the center
            center_x = int(x != 0)
            center_z = int(z != 0)

            # If there is a connection between tiles
            connections = np.zeros(neigh_shp[:-2], dtype=bool)

            # Now we fill the values considering that we might have corner cases:
            # 1. Taking a ramp down:
            if x < N - 1:
                idx_x = neigh_shp[0] - 1

                # We check by seeing if the and the neighbors are the same w.r.t. the tiles
                connections[idx_x, center_z] = np.all(neighborhood[idx_x, center_z, 0, :] <= y[x, z, 1, :])

            # 2. Going right from a ramp
            if z < M - 1:
                idx_z = neigh_shp[1] - 1
                connections[center_x, idx_z] = np.all(neighborhood[center_x, idx_z, :, 0] <= y[x, z, :, 1])

            # 3. Going up from a ramp
            if x > 0:
                connections[0, center_z] = np.all(neighborhood[0, center_z, 1, :] <= y[x, z, 0, :])

            # 4. Going left from a ramp
            if z > 0:
                connections[center_x, 0] = np.all(neighborhood[center_x, 0, :, 1] <= y[x, z, :, 0])

            # Add edges
            edges[z + M * x] = sub_nodes[connections]

    # Transform into a numpy array
    # This array will be useful to identify where to set the objects
    plain_tiles = np.array(plain_tiles)

    return nodes, edges, plain_tiles, lowest_plain_nodes


def get_playable_area(y, enforce_lower_floor=True):
    """
    Returns playable area.

    The algorithm used is dfs to get strongly connected components.
    Then we select the largest strongly connected component to be the "playable area".
    """

    # Get connectivity graph
    nodes, edges, plain_tiles, lowest_plain_nodes = get_connectivity_graph(y)

    # Get connected components
    n_nodes = nodes.shape[0] * nodes.shape[1]
    connected_components = get_connected_components(n_nodes, edges)

    # Get largest connected component
    component_lens = [len(c) for c in connected_components]
    largest_connected_component = connected_components[np.argmax(component_lens)]
    total_area = len(largest_connected_component)

    # Check if the lower floor is fully inside the largest connected component
    # Get lowest floor nodes and then just check if they are inside the largest_connected_component
    if enforce_lower_floor:
        if not np.all([elem in largest_connected_component for elem in lowest_plain_nodes]):
            return None, -1

    # Avoid putting objects in ramps
    plain_idxs = [plain_tiles[i] in largest_connected_component for i in range(len(plain_tiles))]
    largest_connected_component = plain_tiles[plain_idxs]

    # Return indexes of the playable area and if the playable area is larger than
    # the threshold.
    return largest_connected_component, total_area / n_nodes


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


def get_object_fn(obj):
    """
    Returns classes depending on the object.
    """
    if obj == "box":
        return sm.Box

    elif obj == "capsule":
        return sm.Capsule

    elif obj == "sphere":
        return sm.Sphere

    else:
        raise ValueError


def create_objects(positions, object_type=None, specific_color=None, object_size=0.5, rank=0):
    """
    Create objects in simenv.
    """

    object_names = defaultdict(lambda: 0)

    if len(positions) == 0:
        return []

    extra_height = np.array([0, object_size / 2, 0])
    positions = positions + extra_height

    if specific_color is not None:
        color_idx = COLOR_NAMES.index(specific_color)
        colors = [COLORS[color_idx]] * len(positions)
        color_names = [COLOR_NAMES[color_idx]] * len(positions)

    else:
        color_idxs = np.random.choice(np.arange(len(COLORS), dtype=int), size=len(positions), replace=False)
        colors = [COLORS[idx] for idx in color_idxs]
        color_names = [COLOR_NAMES[idx] for idx in color_idxs]

    if object_type is not None:
        objects = [object_type] * len(positions)

    else:
        # Choose among options of objects
        obj_idxs = np.random.choice(np.arange(len(OBJECTS), dtype=int), size=len(positions))
        objects = [OBJECTS[idx] for idx in obj_idxs]

    def increase_and_return(color, obj, n_instance):
        partial_name = color + "_" + obj + "_" + str(n_instance)
        full_name = partial_name + "_" + str(object_names[partial_name])
        object_names[partial_name] += 1
        return full_name

    return [
        get_object_fn(obj)(
            name=increase_and_return(color_name, obj, rank),
            position=pos,
            material=color,
            physics_component=sm.RigidBodyComponent(mass=0.2),
            **get_bounds(object_type=obj, object_size=object_size),
        )
        for pos, color, color_name, obj in zip(positions, colors, color_names, objects)
    ]


# TODO: move this to utils
def get_positions(
    y, n_objects, n_agents, threshold=0.5, distribution="uniform", enforce_lower_floor=True, verbose=False
):
    """
    Returns None if there isn't enough playable area.
    """

    if n_agents == 0 and n_objects == 0:
        return [], [], True

    playable_nodes, area = get_playable_area(y, enforce_lower_floor=enforce_lower_floor)

    if area < 0:
        if verbose:
            print("Lower floor is enforced and not all tiles of this floor are accessible.")
        return None, None, False
    elif area < threshold:
        if verbose:
            print("Unsufficient playable area: {:.3f} when minimum is {}".format(area, threshold))
        return None, None, False

    # Get probabilities to where to place objects
    # TODO: add option to do the same as it's done in XLand from Deepmind
    probabilities = get_distribution(
        get_mask_connected_components(playable_nodes, final_shp=y.shape[:-2]), distribution=distribution
    )

    non_null_nodes = np.sum(probabilities > 0)
    if non_null_nodes < n_objects + n_agents:
        if verbose:
            print(
                "Unsufficient nodes to set objects: {} when the total number of objects"
                "and agents is {}".format(non_null_nodes, n_objects + n_agents)
            )
        return None, None, False

    positions = np.array(sample_index(n_objects + n_agents, probabilities))
    obj_pos, agent_pos = positions[:, :n_objects], positions[:, n_objects:]

    # Return True showing that object placement was successful
    return obj_pos, agent_pos, True
