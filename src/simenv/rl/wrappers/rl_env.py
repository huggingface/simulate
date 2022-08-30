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
from ...scene import Scene


try:
    from stable_baselines3.common.vec_env.base_vec_env import VecEnv
except ImportError:

    class VecEnv:
        pass  # Dummy class if SB3 is not installed


class ParallelRLEnvironment(VecEnv):
    def __init__(self, scene_or_map_fn, n_maps=1, n_show=1, frame_rate=30, frame_skip=4, **engine_kwargs):

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
        self.n_maps = n_maps
        self.n_show = n_show
        self.n_actors_per_map = self.n_actors // self.n_maps

        self.actor = next(iter(self.actors.values()))

        self.action_space = self.scene.action_space # quick workaround while Thom refactors this
        self.observation_space = {
            "CameraSensor": self.scene.observation_space
        }  # quick workaround while Thom refactors this
        self.observation_space = spaces.Dict(self.observation_space)

        super(ParallelRLEnvironment, self).__init__(n_show, self.observation_space, self.action_space)

        # Don't return simulation data, since minimal/faster data will be returned by agent sensors
        # Pass maps kwarg to enable map pooling
        maps = [root.name for root in self.map_roots]
        self.scene.show(
            frame_rate=frame_rate,
            frame_skip=frame_skip,
            return_frames=False,
            return_nodes=False,
            maps=maps,
            n_show=n_show,
        )

    def step(self, action=None):
        action_dict = {}
        # TODO: adapt this to multiagent setting
        if action is None:
            for i in range(self.n_show):
                action_dict[str(i)] = int(self.action_space.sample())
        elif isinstance(action, np.int64):
            action_dict["0"] = int(action)
        else:
            for i in range(self.n_show):
                action_dict[str(i)] = int(action[i])

        event = self.scene.step(action=action_dict)

        # Extract observations, reward, and done from event data
        obs = None
        reward = 0
        done = False
        info = {}
        if self.n_actors == 1:
            actor_data = event["agents"][self.actor.name]
            obs = self._extract_sensor_obs(event["agents"][self.actor.name]["observations"])
            reward = actor_data["reward"]
            done = actor_data["done"]

            return obs, reward, done, info

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

        obs = self._obs_dict_to_tensor(obs)
        reward = np.array(reward)
        done = np.array(done)
        return obs, reward, done, info

    def _extract_sensor_obs(self, obs):
        sensor_obs = {}
        for sensor_name, sensor_data in obs.items():
            if sensor_data["type"] == "uint8":
                shape = sensor_data["shape"]
                measurement = np.array(sensor_data["uintBuffer"], dtype=np.uint8).reshape(shape)
                sensor_obs[sensor_name] = measurement
                pass
            elif sensor_data["type"] == "float":
                shape = sensor_data["shape"]
                measurement = np.array(sensor_data["uintBuffer"], dtype=np.float32).reshape(shape)
                sensor_obs[sensor_name] = measurement
            else:
                raise TypeError

        return sensor_obs

    def _obs_dict_to_tensor(self, obs_dict):
        out = []
        for val in obs_dict.values():
            out.append(val)

        if self.n_agents == 1:
            return {"CameraSensor": np.stack(out)[0]}  # quick workaround while Thom refactors this
        else:
            return {"CameraSensor": np.stack(out)}  # quick workaround while Thom refactors this

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

        obs = self._obs_dict_to_tensor(obs)
        return obs

    def close(self):
        self.scene.close()

    def env_is_wrapped(self):
        return [False] * self.n_agents * self.n_parallel

    # required abstract methods

    def step_async(self, actions: np.ndarray) -> None:
        raise NotImplementedError()

    def env_method(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()

    def seed(self, value):
        # this should be done when the env is initialized
        return
        # raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def step_send(self):
        raise NotImplementedError()

    def step_wait(self):
        raise NotImplementedError()
