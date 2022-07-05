import simenv as sm
import simenv.assets.utils as utils
import time
import matplotlib.pyplot as plt
import numpy as np


scene = sm.Scene(engine="Unity")

root = sm.Asset()

root += sm.Light(
    name="sun", position=[0, 20, 0], intensity=0.9
)
root += sm.Box(name="floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
root += sm.Box(name="wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
root += sm.Box(name="wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
root += sm.Box(name="wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
root += sm.Box(name="wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
root += sm.Box(name="wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
root += sm.Box(name="wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
root += sm.Box(name="wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
root += sm.Box(name="wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])


agent = sm.SimpleRlAgent(camera_width=64, camera_height=40, position=[0.0, 0.0, 0.0])

root += agent
# scene += root
# camera_height = scene.observation_space.shape[1]
# camera_width = scene.observation_space.shape[2]

# get the scene bytes
#map_bytes = scene.as_glb_bytes()
for i in range(8):
    copy = root.copy().translate_x(10*i)
    print(copy)
    copy_bytes = copy.as_glb_bytes()
    scene.engine.add_to_pool(copy_bytes)


scene.engine.activate_environments(4)
input("Press enter to continue")
scene.close()
