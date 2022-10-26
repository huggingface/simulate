from collections import defaultdict
import numpy as np

def compute_connectivity_graph_from_height_map(height_map):
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
    N, M, _, _ = height_map.shape
    nodes = np.arange(N * M).reshape((N, M))
    lowest_plain_nodes = []
    min_height = np.min(np.amax(height_map, axis=(2, 3)))

    # Identify plain tiles to use them to place objects
    plain_tiles = []

    for x in range(N):
        for z in range(M):

            if np.all(height_map[x, z] == height_map[x, z, 0, 0]):
                plain_tiles.append(z + M * x)
                # We check if the plain tile is in the lowest height
                # BUG: there is a bug on the connected components that needs to be solved.
                if height_map[x, z, 0, 0] == min_height:
                    lowest_plain_nodes.append(z + M * x)

            min_x, max_x, min_z, max_z = max(0, x - 1), min(N, x + 2), max(0, z - 1), min(M, z + 2)

            neighborhood = height_map[min_x:max_x, min_z:max_z]
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
                connections[idx_x, center_z] = np.all(neighborhood[idx_x, center_z, 0, :] <= height_map[x, z, 1, :])

            # 2. Going right from a ramp
            if z < M - 1:
                idx_z = neigh_shp[1] - 1
                connections[center_x, idx_z] = np.all(neighborhood[center_x, idx_z, :, 0] <= height_map[x, z, :, 1])

            # 3. Going up from a ramp
            if x > 0:
                connections[0, center_z] = np.all(neighborhood[0, center_z, 1, :] <= height_map[x, z, 0, :])

            # 4. Going left from a ramp
            if z > 0:
                connections[center_x, 0] = np.all(neighborhood[center_x, 0, :, 1] <= height_map[x, z, :, 0])

            # Add edges
            edges[z + M * x] = sub_nodes[connections]

    # Transform into a numpy array
    # This array will be useful to identify where to set the objects
    plain_tiles = np.array(plain_tiles)

    return {
        "nodes": nodes,
        "edges": edges,
        "plain_tiles": plain_tiles,
        "lowest_plain_nodes": lowest_plain_nodes
    }