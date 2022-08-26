import argparse

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


# File inspired by soruce: https://github.com/openai/gym/blob/master/gym/envs/box2d/lunar_lander.py

# CONSTANTS From source
FPS = 50
SCALE = 30.0  # affects how fast-paced the game is, forces should be adjusted as well

MAIN_ENGINE_POWER = 13.0
SIDE_ENGINE_POWER = 0.6

INITIAL_RANDOM = 1000.0  # Set 1500 to make game harder

LANDER_POLY = np.array([(-14, +17, 0), (-17, 0, 0), (-17, -10, 0), (+17, -10, 0), (+17, 0, 0), (+14, +17, 0)]) / SCALE
LEG_AWAY = 20
LEG_DOWN = -7
LEG_ANGLE = 0.25  # radions
LEG_W, LEG_H = 2, 8
LEG_SPRING_TORQUE = 40

SIDE_ENGINE_HEIGHT = 14.0
SIDE_ENGINE_AWAY = 12.0

VIEWPORT_W = 600
VIEWPORT_H = 400

W = VIEWPORT_W / SCALE
H = VIEWPORT_H / SCALE

# terrain
CHUNKS = 11
HEIGHTS = np.random.uniform(0, H / 2, size=(CHUNKS + 1,))
CHUNK_X = [W / (CHUNKS - 1) * i for i in range(CHUNKS)]
HELIPAD_x1 = CHUNK_X[CHUNKS // 2 - 1]
HELIPAD_x2 = CHUNK_X[CHUNKS // 2 + 1]
HELIPAD_y = H / 4
HEIGHTS[CHUNKS // 2 - 2] = HELIPAD_y
HEIGHTS[CHUNKS // 2 - 1] = HELIPAD_y
HEIGHTS[CHUNKS // 2 + 0] = HELIPAD_y
HEIGHTS[CHUNKS // 2 + 1] = HELIPAD_y
HEIGHTS[CHUNKS // 2 + 2] = HELIPAD_y
SMOOTH_Y = [0.33 * (HEIGHTS[i - 1] + HEIGHTS[i + 0] + HEIGHTS[i + 1]) for i in range(CHUNKS)]

LEG_RIGHT_POLY = (
    np.array(
        [
            (LEG_AWAY, LEG_DOWN, 0),
            (LEG_AWAY + LEG_H * np.sin(LEG_ANGLE), LEG_DOWN - LEG_H * np.cos(LEG_ANGLE), 0),
            (
                LEG_AWAY + LEG_H * np.sin(LEG_ANGLE) + LEG_W * np.sin(np.pi / 2 - LEG_ANGLE),
                LEG_DOWN - LEG_H * np.cos(LEG_ANGLE) + LEG_W * np.cos(np.pi / 2 - LEG_ANGLE),
                0,
            ),
            (LEG_AWAY + LEG_W * np.sin(np.pi / 2 - LEG_ANGLE), LEG_DOWN + LEG_W * np.cos(np.pi / 2 - LEG_ANGLE), 0),
        ]
    )
    / SCALE
)

LEG_LEFT_POLY = [(-x, y, z) for x, y, z in LEG_RIGHT_POLY]

LAND_POLY = (
    [(CHUNK_X[0], SMOOTH_Y[0] - 3, 0)]
    + [(x, y, 0) for x, y in zip(CHUNK_X, SMOOTH_Y)]
    + [(CHUNK_X[-1], SMOOTH_Y[0] - 3, 0)]
)
LANDER_COLOR = (128 / 255, 102 / 255, 230 / 255)


def shift_polygon(polygon, shift):
    shifted_poly = [(x + shift[0], y + shift[1], z + shift[2]) for x, y, z in polygon]
    return shifted_poly


def make_lander(engine="Unity", engine_exe=None):
    # Add sm scene
    sc = sm.Scene(engine=engine, engine_exe=engine_exe)

    lander_init_pos = (10, 10, 0) + np.random.uniform(0, 5, 3)
    lander_init_pos[2] = 0.0

    lander_poly_shifted = shift_polygon(LANDER_POLY, lander_init_pos)
    lander_material = sm.Material(base_color=LANDER_COLOR)

    # TODO Add Collider
    lander = sm.Polygon(
        points=lander_poly_shifted,
        material=lander_material,
        name="lunar_lander",
        physics_component=sm.RigidBodyComponent(
            use_gravity=True,
            constraints=[
                # "freeze_position_z",
                # "freeze_rotation_x",
                "freeze_rotation_y",
                "freeze_rotation_z",
            ],
            mass=0.01,
        ),
    )
    lander.mesh.extrude((0, 1, 0), capping=True, inplace=True)

    r_leg_poly_shifted = shift_polygon(LEG_RIGHT_POLY, lander_init_pos)
    r_leg = sm.Polygon(points=r_leg_poly_shifted, material=lander_material, parent=lander, name="lander_r_leg")
    r_leg.mesh.extrude((0, 1, 0), capping=True, inplace=True)

    l_leg_poly_shifted = shift_polygon(LEG_LEFT_POLY, lander_init_pos)
    l_leg = sm.Polygon(points=l_leg_poly_shifted, material=lander_material, parent=lander, name="lander_l_leg")
    l_leg.mesh.extrude((0, 1, 0), capping=True, inplace=True)

    # TODO add collider
    land = sm.Polygon(
        points=LAND_POLY,
        material=sm.Material.GRAY,
        name="Moon",
    )
    land.mesh.extrude((0, 1, 0), capping=True, inplace=True)

    sc += lander
    # sc += r_leg
    # sc += l_leg
    sc += land

    return sc


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument(
        "--show",
        default=False,
        type=bool,
        required=False,
        help="--show=True to show lunarlander in pyvista (and not simulate dynamics)",
    )
    parser.add_argument(
        "--num_steps", default=100, type=int, required=False, help="number of steps to run the simulator"
    )
    args = parser.parse_args()

    if args.show:
        sc = make_lander(engine="pyvista")
        sc.show() #view_vector=(0, 1, 0)
        input("press any key to quit")
    else:
        sc = make_lander(engine="Unity", engine_exe=args.build_exe)
        sc += sm.LightSun()
        sc += sm.Camera(
            name="cam", camera_type="orthographic",
            # TODO Tune position
            position=[0, -5, 0],
            rotation=[0, -30, 0],
            ymag=15, width=256, height=144
        )

        # TODO Add adgent that acts via thrusters (lateral)
        sc.show()

        plt.ion()
        fig, ax = plt.subplots()
        imdata = np.zeros(shape=(144, 256, 3), dtype=np.uint8)
        axim = ax.imshow(imdata, vmin=0, vmax=255)
        # env = sm.RLEnvironment(sc)
        for i in range(1000):
            print(f"step {i}")
            event = sc.step()
            # event, _, _, _ = env.step(action=0)
            if "frames" in event and "cam" in event["frames"]:
                frame = np.array(event["frames"]["cam"], dtype=np.uint8)
                frame = frame.transpose((1, 2, 0))  # (C,H,W) -> (H,W,C)
                axim.set_data(frame)
                fig.canvas.flush_events()
                plt.pause(0.01)
#
# plt.pause(0.5)
#
# pdb.set_trace()
# moon = world.CreateStaticBody(shapes=edgeShape(vertices=[(0, 0), (W, 0)]))
# sky_polys = []
# for i in range(CHUNKS - 1):
#     p1 = (chunk_x[i], smooth_y[i])
#     p2 = (chunk_x[i + 1], smooth_y[i + 1])
#     moon.CreateEdgeFixture(vertices=[p1, p2], density=0, friction=0.1)
#     sky_polys.append([p1, p2, (p2[0], H), (p1[0], H)])
#
# moon.color1 = (0.0, 0.0, 0.0)
# moon.color2 = (0.0, 0.0, 0.0)
#
# initial_y = VIEWPORT_H / SCALE
# lander = world.CreateDynamicBody(
#     position=(VIEWPORT_W / SCALE / 2, initial_y),
#     angle=0.0,
#     fixtures=fixtureDef(
#         shape=polygonShape(vertices=[(x / SCALE, y / SCALE) for x, y in LANDER_POLY]),
#         density=5.0,
#         friction=0.1,
#         categoryBits=0x0010,
#         maskBits=0x001,  # collide only with ground
#         restitution=0.0,
#     ),  # 0.99 bouncy
# )
# lander.color1 = (128, 102, 230)
# lander.color2 = (77, 77, 128)
# lander.ApplyForceToCenter(
#     (
#         np.random.Generator.uniform(-INITIAL_RANDOM, INITIAL_RANDOM),
#         np.random.Generator.uniform(-INITIAL_RANDOM, INITIAL_RANDOM),
#     ),
#     True,
# )
#
# legs = []
# for i in [-1, +1]:
#     leg = world.CreateDynamicBody(
#         position=(VIEWPORT_W / SCALE / 2 - i * LEG_AWAY / SCALE, initial_y),
#         angle=(i * LEG_ANGLE),
#         fixtures=fixtureDef(
#             shape=polygonShape(box=(LEG_W / SCALE, LEG_H / SCALE)),
#             density=1.0,
#             restitution=0.0,
#             categoryBits=0x0020,
#             maskBits=0x001,
#         ),
#     )
#     leg.ground_contact = False
#     leg.color1 = (128, 102, 230)
#     leg.color2 = (77, 77, 128)
#     rjd = revoluteJointDef(
#         bodyA=lander,
#         bodyB=leg,
#         localAnchorA=(0, 0),
#         localAnchorB=(i * LEG_AWAY / SCALE, LEG_DOWN / SCALE),
#         enableMotor=True,
#         enableLimit=True,
#         maxMotorTorque=LEG_SPRING_TORQUE,
#         motorSpeed=+0.3 * i,  # low enough not to jump back into the sky
#     )
#     if i == -1:
#         rjd.lowerAngle = +0.9 - 0.5  # The most esoteric numbers here, angled legs have freedom to travel within
#         rjd.upperAngle = +0.9
#     else:
#         rjd.lowerAngle = -0.9
#         rjd.upperAngle = -0.9 + 0.5
#     leg.joint = world.CreateJoint(rjd)
#     legs.append(leg)
#
# drawlist = [lander] + legs
