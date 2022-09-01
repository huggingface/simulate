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
import numpy as np
from gym import spaces

# Lint as: python3
from simenv.scene import Scene


class RLEnvironment:
    def __init__(self, scene: Scene):

        self.scene = scene

        self.actors = {actor.name: actor for actor in self.scene.actors}
        self.n_actors = len(self.actors)

        self.actor = next(iter(self.actors.values()))

        self.action_space = self.scene.action_space  # quick workaround while Thom refactors this
        self.observation_space = {
            "CameraSensor": self.scene.observation_space
        }  # quick workaround while Thom refactors this
        self.observation_space = spaces.Dict(self.observation_space)

    def show(self):
        self.scene.show()

    def step(self, action: np.ndarray = None):
        if action is None:
            action = self.action_space.sample()
        action_dict = {}

        action_dict["0"] = action

        event = self.scene.step(action=action_dict)

        # Extract observations, reward, and done from event data
        actor_data = event["actors"][self.actor.name]
        obs = self._extract_sensor_obs(actor_data["observations"])
        reward = actor_data["reward"]
        done = actor_data["done"]
        info = {}

        return obs, reward, done, info

    def reset(self):
        self.scene.reset()

        # To extract observations, we do a "fake" step (no actual simulation with frame_skip=0)
        event = self.scene.step(return_frames=True, frame_skip=0)

        actor_data = event["actors"][self.actor.name]
        obs = self._extract_sensor_obs(actor_data["observations"])
        return obs

    def _extract_sensor_obs(self, sim_data):
        sensor_obs = {}
        for sensor_name, sensor_data in sim_data.items():
            if sensor_data["type"] == "uint8":
                shape = sensor_data["shape"]
                measurement = np.array(sensor_data["uintBuffer"], dtype=np.uint8).reshape(shape)
                sensor_obs[sensor_name] = measurement
                pass
            elif sensor_data["type"] == "float":
                shape = sensor_data["shape"]
                measurement = np.array(sensor_data["floatBuffer"], dtype=np.float32).reshape(shape)
                sensor_obs[sensor_name] = measurement
            else:
                raise TypeError

        return sensor_obs

    def close(self):
        self.scene.close()