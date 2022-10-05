from cmath import pi

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import use

import simulate as sm
from simulate.assets import material
from simulate.assets.reward_functions import RewardFunction


scene = sm.Scene(engine="unity", config=sm.Config(time_step=1 / 30.0, frame_skip=4))

scene += sm.LightSun()
scene += sm.Camera(
    name="cam",
    camera_type="orthographic",
    xmag=1,
    ymag=1,
    zfar=100,
    znear=0.001,
    position=[0, 1, -10],
    width=256,
    height=144,
)

# Define a immovable base as the root of the scene (could also just be the scene itself but here we see it)
root = sm.Sphere(name="root", radius=0.01, position=[0, 0, 0], material=sm.Material.BLUE)
root.physics_component = sm.ArticulationBodyComponent("fixed", immovable=True, use_gravity=False)
scene += root

# Pendulum is child of the root
pendulum = sm.Cylinder(
    name="pendulum", position=[0, -0.5, -0.025], height=1, radius=0.01, material=material.Material.RED, is_actor=True
)
pendulum.physics_component = sm.ArticulationBodyComponent("revolute", immovable=False, use_gravity=True)
pendulum.actuator = sm.Actuator(
    low=-2.0,
    high=2.0,
    shape=(1,),
    mapping=sm.ActionMapping("add_torque", axis=[1, 0, 0], amplitude=3, max_velocity_threshold=8.0),
)
root += pendulum

pendulum += sm.StateSensor(root, pendulum, "rotation")

scene.save("test.gltf")

scene2 = sm.Scene.create_from("test.gltf")

env = sm.RLEnv(scene)

for i in range(10):
    event = env.step(action=1.0)
