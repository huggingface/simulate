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

from typing import Callable, Optional, Union

import numpy as np

try:
    from stable_baselines3.common.vec_env.base_vec_env import VecEnv
except ImportError:

    class VecEnv:
        pass  # Dummy class if SB3 is not installed

import simenv as sm
# Lint as: python3
from simenv.scene import Scene


class RLEnv(VecEnv):
    """
    RL environment wrapper for SimEnv scene. Uses functionality from the VecEnv in stable baselines 3
    For more information on VecEnv, see the source
    https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html

    Args:
        scene_or_map_fn: a generator function for generating instances of the desired environment
        n_maps: the number of map instances to create, defualt 1
        n_show: optionally show a subset of the maps during training and dequeue a new map at the end of each episode
        time_step: the physics timestep of the environment
        frame_skip: the number of times an action is repeated before the next observation is returned
    """

    def __init__(
        self,
        scene_or_map_fn: Union[Callable, Scene],
        n_maps: int = 1,
        n_show: int = 1,
        time_step: float = 1 / 30.0,
        frame_skip: int = 4,
        **engine_kwargs,
    ):

        if hasattr(scene_or_map_fn, "__call__"):
            scene_config = sm.Config(
                time_step=time_step,
                frame_skip=frame_skip,
                return_frames=False,
                return_nodes=False,
            )
            self.scene = Scene(engine="Unity", config=scene_config, **engine_kwargs)
            self.scene += sm.LightSun(name="sun", position=[0, 20, 0], intensity=0.9)
            self.map_roots = []
            for i in range(n_maps):
                map_root = scene_or_map_fn(i)
                self.scene += map_root
                self.map_roots.append(map_root)
        else:
            self.scene = scene_or_map_fn
            self.map_roots = [self.scene]

        # TODO --> add warning if scene has no actor or reward functions
        self.actors = {actor.name: actor for actor in self.scene.actors}
        self.n_actors = len(self.actors)
        self.n_maps = n_maps
        self.n_show = n_show
        self.n_actors_per_map = self.n_actors // self.n_maps

        self.actor = next(iter(self.actors.values()))

        self.action_space = self.scene.action_space
        self.observation_space = self.scene.observation_space

        super().__init__(n_show, self.observation_space, self.action_space)

        # Don't return simulation data, since minimal/faster data will be returned by agent sensors
        self.scene.config.time_step = time_step
        self.scene.config.frame_skip = frame_skip
        self.scene.config.return_frames = False
        self.scene.config.return_nodes = False

        # Pass maps kwarg to enable map pooling
        maps = [root.name for root in self.map_roots]
        self.scene.show(
            maps=maps,
            n_show=n_show,
        )

    def step(self, action: Optional[list] = None):
        self.step_send_async(action=action)
        return self.step_recv_async()

    def step_send_async(self, action=None):
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

        self.scene.engine.step_send_async(action=action_dict)

    def step_recv_async(self):
        event = self.scene.engine.step_recv_async()

        # Extract observations, reward, and done from event data
        # TODO nathan thinks we should make this for 1 agent, have a separate one for multiple agents.
        obs = self._extract_sensor_obs(event["actor_sensor_buffers"])
        reward = self._convert_to_numpy(event["actor_reward_buffer"]).flatten()
        done = self._convert_to_numpy(event["actor_done_buffer"]).flatten()

        obs = self._squeeze_actor_dimension(obs)

        return obs, reward, done, [{}] * len(done)

    def _squeeze_actor_dimension(self, obs):
        for k, v in obs.items():
            obs[k] = obs[k].reshape((self.n_show * self.n_actors_per_map, *obs[k].shape[2:]))
        return obs

    def reset(self):
        self.scene.reset()

        # To extract observations, we do a "fake" step (no actual simulation with frame_skip=0)
        event = self.scene.step(return_frames=True, frame_skip=0)
        obs = self._extract_sensor_obs(event["actor_sensor_buffers"])
        obs = self._squeeze_actor_dimension(obs)
        return obs

    def _convert_to_numpy(self, event_data):
        if event_data["type"] == "uint8":
            shape = event_data["shape"]
            return np.array(event_data["uintBuffer"], dtype=np.uint8).reshape(shape)
        elif event_data["type"] == "float":
            shape = event_data["shape"]
            return np.array(event_data["floatBuffer"], dtype=np.float32).reshape(shape)
        else:
            raise TypeError

    def _extract_sensor_obs(self, sim_event_data):
        sensor_obs = {}
        for sensor_name, sensor_data in sim_event_data.items():
            sensor_obs[sensor_name] = self._convert_to_numpy(sensor_data)
        return sensor_obs

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
