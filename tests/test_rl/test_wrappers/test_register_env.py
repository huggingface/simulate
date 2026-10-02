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
""" A very simple test for registering simulate scenes as gym environments"""

import random
import unittest

import gym
import pytest

import simulate as sm


def create_scene():
    """ " Create a simple scene with a single actor and a single target."""
    scene = sm.Scene() + sm.LightSun()
    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-11, 11, 0, 0.1, -11, 51], material=sm.Material.BLUE)
    scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.GRAY)
    scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.GRAY)
    scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.GRAY)
    scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.GRAY)
    collectable = sm.Sphere(position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=sm.Material.GREEN)
    actor = sm.EgocentricCameraActor()
    reward = sm.RewardFunction("sparse", entity_a=actor, entity_b=collectable, is_collectable=True)
    scene += [collectable, actor, reward]
    return scene


class TestRegisterEnv(unittest.TestCase):
    def test_register_env(self):
        scene = create_scene()

        # create environment without gym
        env = sm.RLEnv(scene=scene, time_step=1 / 30.0, frame_skip=4)

        # register environment
        try:
            sm.RLEnv.register("TestRegisterEnv-v0", scene=scene, time_step=1 / 30.0, frame_skip=4)
            gym_env = gym.make("TestRegisterEnv-v0")
        except Exception as e:
            pytest.fail(f"Failed to register environment with exception {e}!")

        # Check if RLEnv is a gym.Env
        assert isinstance(gym_env, gym.Env)

        # This may need to change if sm.RLEnv.register copies the scene before
        assert env.scene == gym_env.scene
