import random

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


scene = sm.Scene(engine="Godot")
scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)

scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-50, 50, 0, 0.1, -50, 50], material=sm.Material.BLUE)
scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.RED)
scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)
scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.RED)

material = sm.Material.GREEN
for i in range(20):
    scene += sm.Box(name=f"cube{i}", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)

material = sm.Material.YELLOW
target = sm.Box(name="cube", position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=material)
scene += target


agent = sm.SimpleActor(name="agent", position=[0.0, 0.0, 0.0])
scene += agent

env = sm.ParallelRLEnvironment(scene)

for i in range(1000):
    action = agent.rl_component.discrete_actions.sample()
    obs, reward, done, info = env.step(action)

    plt.pause(0.1)

scene.close()
