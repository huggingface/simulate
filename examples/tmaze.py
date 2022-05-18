import simenv as sm
import os, time
scene = sm.Scene(engine="Unity")


scene += sm.Light(name="sun", position=[0, 20, 0], rotation=(60, -30, 0), intensity=3.5)

scene += sm.Cube(name="floor", position=[0.0, -0.1, 0.0], rotation=[0.0, 0.0, 0.0, 1.0], scaling=[5.0, 0.05, 5.0])
scene += sm.Cube(name="wall1", position=[-1.0, 0.5, 1.5], rotation=[0.0, 0.0, 0.0, 1.0], scaling=[0.05, 0.5, 3.0])
scene += sm.Cube(name="wall2", position=[1.0, 0.5, 1.5], rotation=[0.0, 0.0, 0.0, 1.0], scaling=[0.05, 0.5, 3.0])
scene += sm.Cube(name="wall3", position=[0.0, 0.5, 4.5], rotation=[0.0, 0.707107, 0.0, 0.707107], scaling=[0.05, 0.5, 1.0])
scene += sm.Cube(name="wall4", position=[2.0, 0.5, -1.5], rotation=[0.0, 0.707107, 0.0, 0.707107], scaling=[0.05, 0.5, 1.0])
scene += sm.Cube(name="wall5", position=[0.0, 0.5, -3.5], rotation=[0.0, 0.707107, 0.0, 0.707107], scaling=[0.05, 0.5, 3.0])
scene += sm.Cube(name="wall6", position=[-2.0, 0.5, -1.5], rotation=[0.0, 0.707107, 0.0, 0.707107], scaling=[0.05, 0.5, 1.0])
scene += sm.Cube(name="wall7", position=[-3.0, 0.5, -2.5], rotation=[0, 1, 0, 0], scaling=[0.05, 0.5, 1.0])
scene += sm.Cube(name="wall8", position=[3.0, 0.5, -2.5], rotation=[0, 1, 0, 0], scaling=[0.05, 0.5, 1.0])


agent = sm.RLAgent(name="agent", position=[0, 0, 0.0])
agent += sm.RLAgentCamera(position=[5, 6.5, -3.75], rotation=(45, -45, 0), width=1024, height=1024)
scene += agent


scene.show()


env = sm.RLEnv(scene)
for i in range(1000):
    action = env.action_space.sample()
    if type(action) == int: # discrete are ints, continuous are numpy arrays
        action = [action]
    else:
        action = action.tolist()

    env.step(action)
    time.sleep(0.5)


scene.close()
