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

import random

# Lint as: python3
import unittest

import simulate as sm


def create_env(dummy_port: int):
    """ " Create a simple environment with a single agent and a single target."""
    scene = sm.Scene() + sm.LightSun()
    scene += sm.Box(name="floor", position=[0, 0, 0], bounds=[-11, 11, 0, 0.1, -11, 51], material=sm.Material.BLUE)
    scene += sm.Box(name="wall1", position=[-10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.GRAY)
    scene += sm.Box(name="wall2", position=[10, 0, 0], bounds=[0, 0.1, 0, 1, -10, 10], material=sm.Material.GRAY)
    scene += sm.Box(name="wall3", position=[0, 0, 10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.GRAY)
    scene += sm.Box(name="wall4", position=[0, 0, -10], bounds=[-10, 10, 0, 1, 0, 0.1], material=sm.Material.GRAY)
    collectable = sm.Sphere(position=[random.uniform(-9, 9), 0.5, random.uniform(-9, 9)], material=sm.Material.GREEN)
    actor, reward = sm.EgocentricCameraActor()
    reward = sm.RewardFunction(collectable, actor, is_collectable=True)
    scene += [collectable, actor, reward]
    return scene


# TODO add a real RL test
class ParallelSimulateTest(unittest.TestCase):
    def test_parallel_simulate(self):
        pass
        # env = sm.ParallelSimulate(env_fn=create_env, n_parallel=2)

        # obs = env.reset()
