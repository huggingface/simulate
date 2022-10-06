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


def generate_map(index):
    root = sm.Asset(name=f"root_{index}")
    root += sm.Box(
        name=f"floor_{index}",
        position=[0, -0.05, 0],
        scaling=[10, 0.1, 10],
        material=sm.Material.BLUE,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall1_{index}",
        position=[-1, 0.5, 0],
        scaling=[0.1, 1, 5.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall2_{index}",
        position=[1, 0.5, 0],
        scaling=[0.1, 1, 5.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall3_{index}",
        position=[0, 0.5, 4.5],
        scaling=[5.9, 1, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall4_{index}",
        position=[-2, 0.5, 2.5],
        scaling=[1.9, 1, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall5_{index}",
        position=[2, 0.5, 2.5],
        scaling=[1.9, 1, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall6_{index}",
        position=[-3, 0.5, 3.5],
        scaling=[0.1, 1, 2.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall7_{index}",
        position=[3, 0.5, 3.5],
        scaling=[0.1, 1, 2.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )
    root += sm.Box(
        name=f"wall8_{index}",
        position=[0, 0.5, -2.5],
        scaling=[1.9, 1, 0.1],
        material=sm.Material.GRAY75,
        with_collider=True,
    )

    collectable = sm.Sphere(name=f"collectable_{index}", position=[2, 0.5, 3.4], radius=0.3, with_collider=True)
    root += collectable

    actor = sm.EgocentricCameraActor(name=f"actor_{index}", position=[0.0, 0.5, 0.0])
    root += actor
    actor += sm.RewardFunction(entity_a=actor, entity_b=collectable, distance_metric="best_euclidean")

    sparse_reward = sm.RewardFunction(
        type="sparse",
        entity_a=actor,
        entity_b=collectable,
        distance_metric="euclidean",
        threshold=0.2,
        is_terminal=True,
        is_collectable=True,
    )

    # varying the timeout to test staggered pooling
    timeout = 200
    timeout_reward = sm.RewardFunction(
        type="timeout",
        distance_metric="euclidean",
        threshold=timeout,
        is_terminal=True,
        scalar=-1.0,
    )
    actor += sparse_reward
    actor += timeout_reward

    return root


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build_exe", default="", type=str, required=False, help="Pre-built unity app for simulate")
    parser.add_argument("--n_maps", default=12, type=int, required=False, help="Number of maps to spawn")
    parser.add_argument("--n_show", default=4, type=int, required=False, help="Number of maps to show")
    args = parser.parse_args()

    env = sm.ParallelRLEnv(generate_map, args.n_maps, args.n_show, engine_exe=args.build_exe)

    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=1)
    model.learn(total_timesteps=100000)

    env.close()
