"""
Utils for dealing with graphs.
"""

from collections import defaultdict


def transpose_graph(edges):
    """
    Transpose graph.
    """

    tranposed_edges = defaultdict(list)

    for i in edges:
        for j in edges[i]:
            tranposed_edges[j].append(i)

    return tranposed_edges


def dfs(v, visited, edges, stack, return_components=False, curr_components=None):
    """
    Depth-first search.

    Includes both versions necessary to get strongly connected components.
    Either it does a normal dfs and returns nothing, or it returns the vertices
    that it went through.
    """

    if return_components:
        if curr_components is None:
            curr_components = [v]
        else:
            curr_components.append(v)

    visited[v] = True

    for i in edges[v]:
        if not visited[i]:
            dfs(i, visited, edges, stack, return_components=return_components, curr_components=curr_components)

    if not return_components:
        stack.append(v)

    else:
        return curr_components


def get_connected_components(n_nodes, edges):
    """
    Gets strongly connected components.

    Implements Korasaju's algorithm.
    """

    # Create stack of visited nodes
    stack = []
    visited = [False] * n_nodes

    for i in range(n_nodes):
        if not visited[i]:
            dfs(i, visited, edges, stack)

    # Transpose graph
    transposed_edges = transpose_graph(edges)

    # Get connected components
    connected_components = []
    visited = [False] * n_nodes

    # Go through transposed graph
    while len(stack) > 0:
        i = stack.pop()
        if not visited[i]:
            component = dfs(i, visited, transposed_edges, stack, return_components=True)
            connected_components.append(component)

    return connected_components
