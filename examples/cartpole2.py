from matplotlib import use
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

cart = sm.Box(name="cart", bounds=[cart_width, cart_height, 1])
cart.physics_component = sm.RigidBodyComponent(mass=1.0, constraints=["freeze_rotation_x", "freeze_rotation_x", "freeze_rotation_z", "freeze_position_y", "freeze_position_z",], use_gravity=False)

mapping = [
    sm.ActionMapping("change_relative_position", axis=[1, 0, 0], amplitude=2.0),
    sm.ActionMapping("change_relative_position", axis=[-1, 0, 0], amplitude=2.0),
]
cart.controller = sm.Controller(n=2, mapping=mapping)

pivot = sm.Box(name="pivot", position=[0,cart_height/2, 0], bounds=[0.1,0.1,0.1])

# for more information on Articulation bodies in Unity https://docs.unity3d.com/Manual/physics-articulations.html
pivot.physics_component = sm.ArticulatedBodyComponent("revolute")
cart += pivot
pole = sm.Box(
    name="pole",
    position=[0, cart_height / 2.0 + pole_height / 2.0, 0],
    bounds=[pole_radius, pole_height, pole_radius],
    rotation=[10, 0, 0],
)
pole.physics_component = sm.ArticulatedBodyComponent("revolute",anchor_position=[0,-pole_height/2, 0])
pivot += pole
cart += sm.StateSensor(pole, cart, "position")


scene += cart
env = sm.RLEnv(scene)


# plt.ion()
# fig, ax = plt.subplots()
# imdata = np.zeros(shape=(144, 256, 3), dtype=np.uint8)
# axim = ax.imshow(imdata, vmin=0, vmax=255)
for i in range(300):
    env.step()
    # if "frames" in event and "cam" in event["frames"]:
    #     frame = np.array(event["frames"]["cam"], dtype=np.uint8)
    #     frame = frame.transpose((1, 2, 0))  # (C,H,W) -> (H,W,C)
#         axim.set_data(frame)
#         fig.canvas.flush_events()
#         plt.pause(0.1)

# plt.pause(0.5)
