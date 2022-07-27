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


def fill_order(v, visited, edges, stack):
    # Create stack for iterative version of algorithm
    internal_stack = [v]
    backtracking_stack = []

    while len(internal_stack) > 0:
        s = internal_stack.pop()

        if not visited[s]:
            visited[s] = True

            for i in edges[s]:
                if not visited[i]:
                    internal_stack.append(i)

            backtracking_stack.append(s)

    backtracking_stack.reverse()
    stack.extend(backtracking_stack)


def dfs(v, visited, edges):
    """
    Depth-first search without recursion.

    Includes both versions necessary to get strongly connected components.
    Either it does a normal dfs and returns nothing, or it returns the vertices
    that it went through.
    """
    # Create stack for iterative version of algorithm
    internal_stack = [v]

    # If we return the components, create the curr_components var
    curr_components = []

    while len(internal_stack) > 0:
        s = internal_stack.pop()

        if not visited[s]:
            visited[s] = True

            for i in edges[s]:
                if not visited[i]:
                    internal_stack.append(i)

            curr_components.append(s)

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
            fill_order(i, visited, edges, stack)

    # Transpose graph
    transposed_edges = transpose_graph(edges)

    # Get connected components
    connected_components = []
    visited = [False] * n_nodes

    # Go through transposed graph
    while len(stack) > 0:
        i = stack.pop()
        if not visited[i]:
            component = dfs(i, visited, transposed_edges)
            connected_components.append(component)

    return connected_components
