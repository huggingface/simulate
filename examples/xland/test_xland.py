from env import XLandEnvironment

import simulate as sm


if __name__ == "__main__":
    env = XLandEnvironment(20, 20, 4)
    scene = sm.Scene(engine="Unity")
    scene += sm.LightSun()
    world = env.generate_new_world()
    scene += world.get_root_object()
    scene.show()
    input("Press enter to end test")
    scene.close()
