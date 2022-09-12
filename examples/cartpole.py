from cmath import pi
from matplotlib import use
import matplotlib.pyplot as plt
import numpy as np

import simenv as sm
from simenv.assets import material
from simenv.assets.reward_functions import RewardFunction


scene = sm.Scene(engine="Unity")

cart_depth = 0.3
cart_width = 0.5
cart_height = 0.2
pole_radius = 0.05
pole_height = 1.0

scene += sm.LightSun()
scene += sm.Camera(
    name="cam", camera_type="orthographic", ymag=15, position=[0, cart_height, -10], width=256, height=144
)

base = sm.Cylinder(name="base", direction=(1, 0, 0), radius=0.05, height=30, material=material.Material.GRAY50)
base.physics_component = sm.ArticulatedBodyComponent(
    "prismatic", immovable=True, use_gravity=False
)  # note for the base the joint type is ignored


cart = sm.Box(name="cart", bounds=[cart_width, cart_height, cart_depth])

cart.physics_component = sm.ArticulatedBodyComponent("prismatic", immovable=False, use_gravity=True)
mapping = [
    sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=10.0),
    sm.ActionMapping("add_force", axis=[-1, 0, 0], amplitude=10.0),
]
cart.controller = sm.Controller(n=2, mapping=mapping)
cart += sm.RewardFunction(
    type="timeout",
    distance_metric="euclidean",
    threshold=100,
    is_terminal=True,
    scalar=-1.0,
)
base += cart
# for more information on Articulation bodies in Unity https://docs.unity3d.com/Manual/physics-articulations.html

pole = sm.Cylinder(
    name="pole",
    position=[0, pole_height / 2.0 + cart_height / 2.0, 0],
    radius=pole_radius,
    height=pole_height,
    rotation=[0, 0, 0],
)
pole.physics_component = sm.ArticulatedBodyComponent(
    "revolute", anchor_position=[0, -pole_height / 2, 0], anchor_rotation=[0, 1, 0, 1]
)
cart += pole
cart += sm.StateSensor(pole, cart, "position")

# not_reward = sm.RewardFunction("not", is_terminal=True)
cart += sm.RewardFunction(
    type="angle_to",
    entity_a=pole,
    entity_b=cart,
    direction=[1, 0, 0],
    distance_metric="euclidean",
    threshold=60,
    is_terminal=True,
    scalar=1.0,
)
cart += sm.RewardFunction(
    type="angle_to",
    entity_a=pole,
    entity_b=cart,
    direction=[-1, 0, 0],
    distance_metric="euclidean",
    threshold=60,
    is_terminal=True,
    scalar=1.0,
)

scene += base
env = sm.RLEnv(scene, frame_skip=1)


# plt.ion()
# fig, ax = plt.subplots()
# imdata = np.zeros(shape=(144, 256, 3), dtype=np.uint8)
# axim = ax.imshow(imdata, vmin=0, vmax=255)
for i in range(10000):
    env.step()
    # if "frames" in event and "cam" in event["frames"]:
    #     frame = np.array(event["frames"]["cam"], dtype=np.uint8)
    #     frame = frame.transpose((1, 2, 0))  # (C,H,W) -> (H,W,C)
#         axim.set_data(frame)
#         fig.canvas.flush_events()
#         plt.pause(0.1)

# plt.pause(0.5)
