import argparse

import matplotlib.pyplot as plt
import numpy as np

import simenv as sm


# File inspired by soruce: https://github.com/openai/gym/blob/master/gym/envs/box2d/lunar_lander.py

# CONSTANTS From source
# TODO implement scaling
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

LEG_LEFT_POLY = [[-x, y, z] for x, y, z in LEG_RIGHT_POLY]

LAND_POLY = (
    [[CHUNK_X[0], SMOOTH_Y[0] - 3, 0]]
    + [[x, y, 0] for x, y in zip(CHUNK_X, SMOOTH_Y)]
    + [[CHUNK_X[-1], SMOOTH_Y[0] - 3, 0]]
)
LANDER_COLOR = [128 / 255, 102 / 255, 230 / 255]


def shift_polygon(polygon, shift):
    shifted_poly = [[x + shift[0], y + shift[1], z + shift[2]] for x, y, z in polygon]
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
        points=LANDER_POLY,  # lander_poly_shifted,
        material=lander_material,
        position=lander_init_pos,
        name="lunar_lander",
        physics_component=sm.RigidBodyComponent(
            use_gravity=True,
            constraints=[
                "freeze_rotation_y",
                "freeze_rotation_z",
            ],
            mass=1,
        ),
    )
    lander.mesh.extrude((0, 0, 1), capping=True, inplace=True)
    lander.actuator = sm.Actuator(
        mapping=[
            sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=1),
            sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=-1),
            sm.ActionMapping("add_force", axis=[0, 1, 0], amplitude=0.3),
        ],
        n=3,
    )

    # TODO add lander state sensors for state-based RL

    r_leg = sm.Polygon(points=LEG_RIGHT_POLY, material=lander_material, parent=lander, name="lander_r_leg")
    r_leg.mesh.extrude((0, 0, 1), capping=True, inplace=True)
    r_leg.collider = sm.Collider(type="mesh", convex=True, mesh=r_leg.mesh)

    l_leg = sm.Polygon(
        points=LEG_LEFT_POLY, material=lander_material, parent=lander, name="lander_l_leg"  # l_leg_poly_shifted,
    )
    l_leg.mesh.extrude((0, 0, 1), capping=True, inplace=True)
    l_leg.collider = sm.Collider(type="mesh", convex=True, mesh=l_leg.mesh)

    lander.collider = sm.Collider(type="mesh", convex=True, mesh=lander.mesh)
    # TODO verify collider
    land = sm.Polygon(
        points=LAND_POLY,
        material=sm.Material.GRAY,
        name="Moon",
    )
    land.mesh.extrude((0, 0, 1), capping=True, inplace=True)
    land.collider = sm.Collider(type="mesh", convex=True, mesh=land.mesh)

    lander += sm.Camera(
        name="cam",
        camera_type="orthographic",
        # TODO Tune position
        position=np.array([10, 12, 3]) - lander_init_pos,
        rotation=[0, -180, 0],
        ymag=10,
        width=256,
        height=256,
    )

    sc += lander
    sc += land

    return sc


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default=None, type=str, required=False, help="Pre-built unity app for simenv")
    parser.add_argument(
        "--num_steps", default=100, type=int, required=False, help="number of steps to run the simulator"
    )
    parser.add_argument("--plot", default=False, type=bool, required=False, help="show camera in matplotlib")

    args = parser.parse_args()

    sc = make_lander(engine="Unity", engine_exe=args.build_exe)
    sc += sm.LightSun()

    sc.show(show_frames=True)

    if args.plot:
        plt.ion()
        fig, ax = plt.subplots()
        imdata = np.zeros(shape=(256, 256, 3), dtype=np.uint8)
        axim = ax.imshow(imdata, vmin=0, vmax=255)
        env = sm.RLEnv(sc)

    for i in range(500):
        print(f"step {i}")
        action = sc.action_space.sample()
        obs, reward, done, info = env.step([action])
        if "CameraSensor" in obs:
            frame = np.array(obs["CameraSensor"], dtype=np.uint8)
            frame = frame.transpose((1, 2, 0))  # (C,H,W) -> (H,W,C)
            if args.plot:
                axim.set_data(frame[::-1])
                fig.canvas.flush_events()
                plt.pause(0.001)
