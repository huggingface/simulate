from env import XLandEnvironment

import simulate as sm


if __name__ == "__main__":
    env = XLandEnvironment(map_width=20, map_height=20, n_maps=1, max_map_level=4)
    scene = sm.Scene(engine="Unity")
    scene += sm.LightSun()
    world = env.generate_new_world()
    scene += world.get_root_object()
    scene.show()
    scene.close()
