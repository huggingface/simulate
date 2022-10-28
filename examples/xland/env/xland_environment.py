from examples.xland.env.world_generation import World
class XLandEnvironment:
    def __init__(self, map_width, map_height, max_map_level=4):
        self.__map_width = map_width
        self.__map_height = map_height
        self.__max_map_level = max_map_level
        # TODO: Generate n worlds
        # TODO: Generate goals
        # TODO: Generate simulate.RLEnv (yield generator)

    def generate_new_world(self):
        return World(
            self.__map_width,
            self.__map_height,
            self.__max_map_level,
        )


