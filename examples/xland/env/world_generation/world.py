import numpy as np

import simulate as sm

from .topology.tiles_generation import generate_tiles_settings
from .topology.utils.compute_connectivity_graph_from_height_map import compute_connectivity_graph_from_height_map
from .topology.utils.graph_search import get_connected_components


class World:
    def __init__(self, map_width, map_height, max_map_level, min_playable_area_size=0.1,
                 require_full_lower_floor_accessible=False):
        self.__map_width = map_width
        self.__map_height = map_height
        self.__tiles_settings = generate_tiles_settings(max_map_level, double_ramp=False)
        self.__wfc_args = {
            "periodic_output": False,
            "periodic_input": False,
            "ground": False,
            "nb_samples": 1,
            "symmetry": 4,
            "verbose": True,
        }
        self.__min_playable_area_size = min_playable_area_size
        self.__require_full_lower_floor_accessible = require_full_lower_floor_accessible
        self.__topology_grid = None

    def mutate_from_existing(self, previous_world):
        '''
        TODO: mutate objects/agents distributions?
        '''
        self.generate(previous_world.__topology_grid.map_2d)

    def generate(self, conditioning_topology=None, nb_attemps=100):
        # Generate a playable topology
        _attempt = 1
        while True:
            # 1) generate topology using WFC
            simulate_topology_grid = self.__generate_topology(conditioning_topology)
            # 2) Assert topology is playable
            #   a) Compute connectivity graph for this topology
            graph = self.__compute_connectivity_graph(simulate_topology_grid.map_2d)
            #   b) Get the largest connected component of this graph
            largest_connected_component = self.__get_largest_connected_component(graph)
            #   c) Assert this graph matches requirements
            if self.__assert_topology_is_playable(graph, largest_connected_component):
                break
            elif _attempt >= nb_attemps:
                raise Exception(f"Unable to generate playable topology in {nb_attemps} attempts.")
            _attempt += 1
            # conditioning_topology = simulate_topology_grid.map_2d

        self.__topology_grid = simulate_topology_grid
        self.__topology_graph = graph
        # Position objects and agents
        # First remove ramps from nodes objects can be put on
        self.__playable_topology_subgraph = [tile for tile in graph["plain_tiles"]
                                             if tile in largest_connected_component]
        # TODO: Implement other distributions than uniform for objects and agents (e.g. CPPN)
        self.__position_objects()
        self.__position_agents()
        self.__topology_grid.generate_3D()
        # TODO: Add walls and colliders

    def get_root_object(self):
        return self.__topology_grid

    def __generate_topology(self, conditioning_topology=None):
         return sm.ProcGenGrid(
            width=self.__map_width,
            height=self.__map_height,
            sample_map=conditioning_topology,
            tiles=self.__tiles_settings["tiles"],
            symmetries=self.__tiles_settings["symmetries"],
            weights=self.__tiles_settings["weights"],
            neighbors=self.__tiles_settings["neighbors"],
            algorithm_args=self.__wfc_args
        )

    def __compute_connectivity_graph(self, height_map):
        return compute_connectivity_graph_from_height_map(height_map)

    def __get_largest_connected_component(self, graph):
        # Get connected components
        n_nodes = graph["nodes"].shape[0] * graph["nodes"].shape[1]
        connected_components = get_connected_components(n_nodes, graph["edges"])

        # Get largest connected component
        component_lens = [len(c) for c in connected_components]
        largest_connected_component = connected_components[np.argmax(component_lens)]

        return largest_connected_component

    def __assert_topology_is_playable(self, graph, largest_connected_component):
        if self.__require_full_lower_floor_accessible:
            if not np.all([node in largest_connected_component for node in graph["lowest_plain_nodes"]]):
                return False

        n_nodes = graph["nodes"].shape[0] * graph["nodes"].shape[1]
        playable_area_size = len(largest_connected_component) / n_nodes
        if playable_area_size < self.__min_playable_area_size:
            return False

        return True

    def __position_objects(self):
        pass

    def __position_agents(self):
        pass