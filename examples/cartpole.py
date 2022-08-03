import os
import time

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


scene = sm.Scene(engine="Unity")

cart_width = 5
cart_height = 3
pole_radius = 0.15
pole_height = 7

scene += sm.LightSun()
scene += sm.Camera(
    name="cam", camera_type="orthographic", ymag=15, position=[0, cart_height, -10], width=256, height=144
)

cart = sm.Box(name="cart", scaling=[cart_width, cart_height, 1])
cart.physics_component = sm.RigidBodyComponent(
    use_gravity=False,
    kinematic=True,
    constraints=[
        "freeze_position_z",
        "freeze_rotation_x",
        "freeze_rotation_y",
        "freeze_rotation_z",
    ],
)

pole = sm.Box(
    name="pole",
    position=[0, cart_height / 2.0 + pole_height / 2.0, 0],
    scaling=[pole_radius, pole_height, pole_radius],
    rotation=[0, 0, 5],
)
pole.physics_component = sm.RigidBodyComponent(
    constraints=[
        "freeze_position_z",
        "freeze_rotation_x",
        "freeze_rotation_y",
    ],
)

scene += cart
scene += pole

scene.show()

plt.ion()
fig, ax = plt.subplots()
imdata = np.zeros(shape=(144, 256, 3), dtype=np.uint8)
axim = ax.imshow(imdata, vmin=0, vmax=255)
for i in range(300):
    event = scene.step()
    if "frames" in event and "cam" in event["frames"]:
        frame = np.array(event["frames"]["cam"], dtype=np.uint8)
        frame = frame.transpose((1, 2, 0))  # (C,H,W) -> (H,W,C)
        axim.set_data(frame)
        fig.canvas.flush_events()
    time.sleep(1 / 30.0)

os.system("pause")
