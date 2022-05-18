import simenv as sm
import simenv.assets.utils as utils
import os, time
from simenv.rl_env import RL_Env
scene = sm.Scene(engine="Unity")


scene += sm.DirectionalLight(
    "sun", translation=[0, 20, 0], rotation=utils.quat_from_degrees(60, -30, 0), intensity=3.5
)
scene += sm.Cube("floor", dynamic=False, translation=[0, -0.05, 0], scale=[100, 0.1, 100])
scene += sm.Cube("wall1", dynamic=False, translation=[-1, 0.5, 0], scale=[0.1, 1, 5.1])
scene += sm.Cube("wall2", dynamic=False, translation=[1, 0.5, 0], scale=[0.1, 1, 5.1])
scene += sm.Cube("wall3", dynamic=False, translation=[0, 0.5, 4.5], scale=[5.9, 1, 0.1])
scene += sm.Cube("wall4", dynamic=False, translation=[-2, 0.5, 2.5], scale=[1.9, 1, 0.1])
scene += sm.Cube("wall5", dynamic=False, translation=[2, 0.5, 2.5], scale=[1.9, 1, 0.1])
scene += sm.Cube("wall6", dynamic=False, translation=[-3, 0.5, 3.5], scale=[0.1, 1, 2.1])
scene += sm.Cube("wall7", dynamic=False, translation=[3, 0.5, 3.5], scale=[0.1, 1, 2.1])
scene += sm.Cube("wall8", dynamic=False, translation=[0, 0.5, -2.5], scale=[1.9, 1, 0.1])


agent = sm.RL_Agent("agent", translation=[0, 0, 0.0])
agent += sm.Camera(
    "cam1", translation=[5, 6.5, -3.75], rotation=utils.quat_from_degrees(45, -45, 0), width=1024, height=1024
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