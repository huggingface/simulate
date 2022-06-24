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


def dfs(v, visited, edges, stack, return_components=False):
    """
    Depth-first search without recursion.

    Includes both versions necessary to get strongly connected components.
    Either it does a normal dfs and returns nothing, or it returns the vertices
    that it went through.
    """
    # Create stack for iterative version of algorithm
    internal_stack = [v]

    # If we return the components, create the curr_components var
    if return_components:
        curr_components = []

    while len(internal_stack) > 0:
        s = internal_stack.pop()

        if not visited[s]:
            visited[s] = True

            for i in edges[s]:
                if not visited[i]:
                    internal_stack.append(i)

            if return_components:
                curr_components.append(s)
            else:
                stack.append(s)

    if return_components:
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
