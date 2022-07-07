import simenv as sm
import os
import time


scene = sm.Scene(engine="Unity")

cart_width = 5
cart_height = 3
pole_radius = 0.15
pole_height = 7

scene += sm.Light()
scene += sm.Camera(camera_type="orthographic", ymag=15, position=[0, cart_height, -10], width=1920, height=1080)

cart = sm.Box(name="cart", scaling=[cart_width, cart_height, 1])
cart.physics_component = sm.RigidBody(
    use_gravity=False,
    kinematic=True,
    constraints=[
        "freeze_position_z",
        "freeze_rotation_x",
        "freeze_rotation_y",
        "freeze_rotation_z",
    ],
)

pole = sm.Box(name="pole", position=[0, cart_height / 2. + pole_height / 2., 0], scaling=[pole_radius, pole_height, pole_radius])
pole.physics_component = sm.RigidBody(
    constraints=[
        "freeze_position_z",
        "freeze_rotation_x",
        "freeze_rotation_y",
    ],
)

scene += cart
scene += pole

scene.show()

for i in range(300):
    scene.step()
    scene.render(path=os.path.abspath(f"output/{i}.png"))
    time.sleep(1 / 30.)

os.system('pause')
