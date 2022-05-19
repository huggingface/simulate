import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RL_Env
scene = sm.Scene(engine="Unity")


scene += sm.Light(
    "sun", position=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
)
scene += sm.Cube("floor", position=[0, -0.05, 0], scaling=[100, 0.1, 100])
scene += sm.Cube("wall1", position=[-1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Cube("wall2", position=[1, 0.5, 0], scaling=[0.1, 1, 5.1])
scene += sm.Cube("wall3", position=[0, 0.5, 4.5], scaling=[5.9, 1, 0.1])
scene += sm.Cube("wall4", position=[-2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Cube("wall5", position=[2, 0.5, 2.5], scaling=[1.9, 1, 0.1])
scene += sm.Cube("wall6", position=[-3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Cube("wall7", position=[3, 0.5, 3.5], scaling=[0.1, 1, 2.1])
scene += sm.Cube("wall8", position=[0, 0.5, -2.5], scaling=[1.9, 1, 0.1])


agent = sm.RL_Agent("agent", position=[0, 0, 0.0])
agent += sm.Camera(
    "cam1", position=[5, 6.5, -3.75], rotation=utils.quat_from_degrees(45, -45, 0), width=1024, height=1024
)
scene += agent


scene.build()


env = RL_Env(scene)
for i in range(1000):
    action = env.action_space.sample()
    if type(action) == int: # discrete are ints, continuous are numpy arrays
        action = [action]
    else:
        action = action.tolist()

    env.step(action)
    time.sleep(0.5)


scene.close()