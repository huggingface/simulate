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
"""Wrapper around SimEnv scene for easier RL training"""

import gym
import numpy as np
from gym import spaces

# Lint as: python3
from ...scene import Scene


class RLEnvironment(gym.Env):
    def __init__(self, scene_or_map_fn, n_maps=1, n_show=1, **engine_kwargs):
        super(RLEnvironment, self).__init__()

        if hasattr(scene_or_map_fn, "__call__"):
            self.scene = Scene(engine="Unity", **engine_kwargs)
            self.map_roots = []
            for i in range(n_maps):
                map_root = scene_or_map_fn(i)
                self.scene += map_root
                self.map_roots.append(map_root)
        else:
            self.scene = scene_or_map_fn
            self.map_roots = [self.scene]

        self.actors = {actor.name: actor for actor in self.scene.actors}
        self.n_actors = len(self.actors)

        self.actor = next(iter(self.actors.values()))

        self.action_space = self.scene.action_space
        self.observation_space = self.scene.observation_space
        # for actor in self.actors.values():
        #     self.observation_space[actor.camera.name] = actor.observation_space
        # self.observation_space = spaces.Dict(self.observation_space)

        # Don't return simulation data, since minimal/faster data will be returned by actor sensors
        # Pass maps kwarg to enable map pooling
        maps = [root.name for root in self.map_roots]
        self.scene.show(frame_rate=30, frame_skip=4, return_frames=False, return_nodes=False, maps=maps, n_show=n_show)

    def step(self, action=None):
        action_dict = {}
        if action is None:
            for actor_name in self.actors.keys():
                action_dict[actor_name] = int(self.action_space.sample())
        elif isinstance(action, dict):
            action_dict = int(action)
        else:
            for actor_name in self.actors.keys():
                action_dict[actor_name] = int(action)
        event = self.scene.step(action=action_dict)

        # Extract observations, reward, and done from event data
        obs = {}
        reward = 0
        done = False
        info = {}
        if self.n_actors == 1:
            actor_data = event["actors"][self.actor.name]
            camera_obs = np.array(actor_data["frames"][self.actor.camera.name], dtype=np.uint8)
            obs[self.actor.camera.name] = camera_obs
            reward = actor_data["reward"]
            done = actor_data["done"]
        else:
            reward = []
            done = []
            info = []
            for actor_name in event["actors"].keys():
                actor = self.actors[actor_name]
                actor_data = event["actors"][actor_name]
                camera_obs = np.array(actor_data["frames"][actor.camera.name], dtype=np.uint8)
                obs[actor.camera.name] = camera_obs
                reward.append(actor_data["reward"])
                done.append(actor_data["done"])
                info.append({})

        return obs, reward, done, info

    def reset(self):
        self.scene.reset()

        # To extract observations, we do a "fake" step (no actual simulation with frame_skip=0)
        event = self.scene.step(return_frames=True, frame_skip=0)
        obs = {}
        if self.n_actors == 1:
            camera_obs = np.array(event["frames"][self.actor.camera.name], dtype=np.uint8)
            obs[self.actor.camera.name] = camera_obs
        else:
            for actor_name in event["actors"].keys():
                actor = self.actors[actor_name]
                camera_obs = np.array(event["frames"][actor.camera.name], dtype=np.uint8)
                obs[actor.camera.name] = camera_obs

        return obs

    def close(self):
        self.scene.close()
