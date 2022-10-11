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

import argparse

from stable_baselines3 import PPO

import simulate as sm
from simulate.assets.action_mapping import ActionMapping


# This example adds an impressive recreation of the mountain car Gym environment


def add_rl_components_to_scene(scene):
    actor = scene.Cart
    actor.is_actor = True

    # Add action mappings, moving left and right
    mapping = [
        ActionMapping("add_force", axis=[1, 0, 0], amplitude=300),
        ActionMapping("add_force", axis=[-1, 0, 0], amplitude=300),
    ]
    actor.actuator = sm.Actuator(mapping=mapping, n=2)

    # Add rewards, reaching the top of the right hill
    reward_entity = sm.Asset(name="reward_entity", position=[-40, 21, 0])
    scene += reward_entity
    reward = sm.RewardFunction(entity_a=reward_entity, entity_b=actor)
    actor += reward

    # Add state sensor, for position of agent
    actor += sm.StateSensor(target_entity=actor, properties=["position"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build_exe", help="path to unity engine build executable", required=False, type=str, default=""
    )
    parser.add_argument("-n", "--n_frames", help="number of frames to simulate", required=False, type=int, default=30)
    args = parser.parse_args()

    build_exe = args.build_exe if args.build_exe != "None" else None
    scene = sm.Scene.create_from("simulate-tests/MountainCar/MountainCar.gltf", engine="unity", engine_exe=build_exe)
    add_rl_components_to_scene(scene)

    env = sm.RLEnv(scene)
    model = PPO("MultiInputPolicy", env, verbose=3, n_epochs=2)
    model.learn(total_timesteps=10000)
