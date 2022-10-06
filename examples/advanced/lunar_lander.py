# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File inspired by source: https://github.com/openai/gym/blob/master/gym/envs/box2d/lunar_lander.py

import argparse
import time

import numpy as np

import simulate as sm


# This example reimplements the famous lunar lander reinforcement learning environment.

# CONSTANTS From source
# TODO implement scaling
SCALE = 30.0  # affects how fast-paced the game is, forces should be adjusted as well

# TODO integrate random initial forces
INITIAL_RANDOM = 1000.0  # Set 1500 to make game harder

# Lander construction
LANDER_POLY = np.array([(-17, -10, 0), (-17, 0, 0), (-14, 17, 0), (14, 17, 0), (17, 0, 0), (17, -10, 0)])[::-1] / SCALE
LEG_AWAY = 20
LEG_DOWN = -7
LEG_ANGLE = 0.25  # radians
LEG_W, LEG_H = 2, 8

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

LEG_LEFT_POLY = [[-x, y, z] for x, y, z in LEG_RIGHT_POLY][::-1]
LANDER_COLOR = [128 / 255, 102 / 255, 230 / 255]

# terrain construction
VIEWPORT_W = 600  # TODO integrate camera with these exact dimensions
VIEWPORT_H = 400

W = VIEWPORT_W / SCALE
H = VIEWPORT_H / SCALE

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

# advanced features
MAIN_ENGINE_POWER = 13.0  # TODO integrate specific forces
SIDE_ENGINE_POWER = 0.6  # TODO integrate specific forces
LEG_SPRING_TORQUE = 40  # TODO integrate specific forces
SIDE_ENGINE_HEIGHT = 14.0  # TODO integrate specific forces
SIDE_ENGINE_AWAY = 12.0  # TODO integrate specific forces

LAND_POLY = (
    [[CHUNK_X[0], SMOOTH_Y[0] - 3, 0]]
    + [[x, y, 0] for x, y in zip(CHUNK_X, SMOOTH_Y)]
    + [[CHUNK_X[-1], SMOOTH_Y[0] - 3, 0]]
)


def make_lander(engine="unity", engine_exe=""):
    # Add sm scene
    sc = sm.Scene(engine=engine, engine_exe=engine_exe)

    # initial lander position sampling
    lander_init_pos = (10, 15, 0) + np.random.uniform(2, 4, 3)
    lander_init_pos[2] = 0.0  # z axis is always 0, for 2D

    lander_material = sm.Material(base_color=LANDER_COLOR)

    # create the lander polygons

    # first, the main lander body
    lander = sm.Polygon(
        points=LANDER_POLY,
        material=lander_material,
        position=lander_init_pos,
        name="lunar_lander",
        is_actor=True,
        physics_component=sm.RigidBodyComponent(
            use_gravity=True,
            constraints=["freeze_rotation_x", "freeze_rotation_y", "freeze_position_z"],
            mass=1,
        ),
    )

    # extrude to make 3D visually.
    lander.mesh.extrude((0, 0, -1), capping=True, inplace=True)
    lander.actuator = sm.Actuator(
        mapping=[
            sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=5),
            sm.ActionMapping("add_force", axis=[1, 0, 0], amplitude=-5),
            sm.ActionMapping("add_force", axis=[0, 1, 0], amplitude=2.5),
        ],
        n=3,
    )

    # add an invisible box as collider until convex meshes are completed
    lander += sm.Box(
        position=[0, np.min(LEG_RIGHT_POLY, axis=0)[1], -0.5],
        bounds=[0.1, 2 * np.max(LEG_RIGHT_POLY, axis=0)[0], 1],
        material=sm.Material.TRANSPARENT,
        rotation=[0, 0, 90],
        with_collider=True,
        name="lander_collider_box_bottom",
    )
    lander += sm.Box(
        position=[-0.6, 0, -0.5],
        bounds=[0.1, 26 / SCALE, 1],
        material=sm.Material.TRANSPARENT,
        rotation=[0, 0, -15],
        with_collider=True,
        name="lander_collider_box_right",
    )
    lander += sm.Box(
        position=[0.6, 0, -0.5],
        bounds=[0.1, 26 / SCALE, 1],
        material=sm.Material.TRANSPARENT,
        rotation=[0, 0, 15],
        with_collider=True,
        name="lander_collider_box_left",
    )

    # add legs as children objects (they take positions as local coordinates!)
    r_leg = sm.Polygon(
        points=LEG_RIGHT_POLY,
        material=lander_material,
        parent=lander,
        name="lander_r_leg",
        # with_collider=True, # TODO can use this when convex colliders is added
    )
    r_leg.mesh.extrude((0, 0, -1), capping=True, inplace=True)

    l_leg = sm.Polygon(
        points=LEG_LEFT_POLY,
        material=lander_material,
        parent=lander,
        name="lander_l_leg",
        # with_collider=True, # TODO can use this when convex colliders is added
    )
    l_leg.mesh.extrude((0, 0, -1), capping=True, inplace=True)

    # Create land object
    land = sm.Polygon(
        points=LAND_POLY[::-1],  # Reversing vertex order so the normal faces the right direction
        material=sm.Material.GRAY,
        name="Moon",
    )
    land.mesh.extrude((0, 0, -1), capping=True, inplace=True)

    # Create collider blocks for the land (non-convex meshes are TODO)
    for i in range(len(CHUNK_X) - 1):
        x1, x2 = CHUNK_X[i], CHUNK_X[i + 1]
        y1, y2 = SMOOTH_Y[i], SMOOTH_Y[i + 1]

        # compute rotation from generated coordinates
        rotation = [0, 0, +90 + np.degrees(np.arctan2(y2 - (y1 + y2) / 2, (x2 - x1) / 2))]
        block_i = sm.Box(
            position=[(x1 + x2) / 2, (y1 + y2) / 2, -0.5],
            bounds=[0.2, 1.025 * np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 1],  # adjustment for better colliders
            material=sm.Material.GRAY,
            rotation=rotation,
            with_collider=True,
            name="land_collider_" + str(i),
        )
        sc += block_i

    # add target triangle / cone for reward
    sc += sm.Cone(
        position=[(HELIPAD_x1 + HELIPAD_x2) / 2, HELIPAD_y, -0.5],
        height=10 / SCALE,
        radius=10 / SCALE,
        material=sm.Material.YELLOW,
        name="target",
    )

    # TODO add lander state sensors for state-based RL
    sc += sm.StateSensor(
        target_entity=sc.target,
        reference_entity=lander,
        properties=["position", "rotation", "distance"],
        name="goal_sense",
    )

    # create Euclidean distance reward, scalar changes the reward to a cost
    cost = sm.RewardFunction(
        type="dense", entity_a=lander, entity_b=sc.target, scalar=-1
    )  # By default a dense reward equal to the distance between 2 entities
    lander += cost

    sc += lander
    sc += land

    return sc


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument(
        "--num_steps", default=100, type=int, required=False, help="number of steps to run the simulator"
    )
    args = parser.parse_args()

    sc = make_lander(engine="unity", engine_exe=args.build_exe)
    sc += sm.LightSun()

    env = sm.RLEnv(sc, frame_skip=1)
    env.reset()

    for i in range(500):
        action = [sc.action_space.sample()]
        obs, reward, done, info = env.step(action)
        print(f"step {i}, reward {reward[0]}")
        time.sleep(0.1)

    env.close()
