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

# Lint as: python3

import argparse

from simulate import logging


logger = logging.get_logger(__name__)

try:
    from stable_baselines3 import PPO
except ImportError:
    logger.warning(
        "stable-baseline3 is required for this example and is not installed. To install: pip install simulate[sb3]"
    )
    exit()

import simulate as sm


CAMERA_HEIGHT = 40
CAMERA_WIDTH = 64


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")
    root += sm.Box(
        name=f"floor_{index}",
        position=[0, 0, 0],
        bounds=[-10, 10, 0, 0.1, -10, 10],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall1_{index}",
        position=[-10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall2_{index}",
        position=[10, 0, 0],
        bounds=[0, 0.1, 0, 1, -10, 10],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall3_{index}",
        position=[0, 0, 10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall4_{index}",
        position=[0, 0, -10],
        bounds=[-10, 10, 0, 1, 0, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )

    actor = sm.EgocentricCameraActor(position=[0.0, 0.5, 0.0], camera_width=64, camera_height=40)
    root += actor
    mass = 0.2
    target = sm.Box(
        name=f"target_{index}",
        position=[-2, 0.5, 2],
        material=sm.Material.RED,
        physics_component=sm.RigidBodyComponent(mass=mass),
    )
    root += target
    target_reward = sm.RewardFunction(
        type="see",
        entity_a=actor,
        entity_b=target,
        distance_metric="euclidean",
        threshold=30.0,
        is_terminal=True,
        is_collectable=True,
        scalar=1.0,
        trigger_once=True,
    )
    actor += target_reward

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument("--n_maps", default=12, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = sm.ParallelRLEnv(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe)

    # for i in range(1000):
    #     obs, reward, done, info = env.step()
    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000)

    env.close()
