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
"""RL Wrapper for scenes with multiple parallel agents"""

from collections import OrderedDict
from copy import deepcopy

import numpy as np
from gym import spaces
from stable_baselines3.common.vec_env.base_vec_env import VecEnv, VecEnvObs
from stable_baselines3.common.vec_env.util import copy_obs_dict, dict_to_obs, obs_space_info


# Lint as: python3


class ParallelEnvironment(VecEnv):
    def __init__(self, scene_fns):
        self.scenes = [scene_fn() for scene_fn in scene_fns]
        agents = self.scenes[0].agents

        if len(agents) == 0:
            print("No agent found. Add at least one agent to the scene")
            return

        agent = agents[0]
        self.action_space = None
        if agent.rl_component.discrete_actions is not None:
            self.action_space = agent.rl_component.discrete_actions
        elif agent.rl_component.box_actions is not None:
            self.action_space = agent.rl_component.box_actions
        if self.action_space is None:
            print("Action space not found. Does the environment contain an agent with an action space?")

        camera = agent.rl_component.camera_sensors[0].camera
        self.observation_space = spaces.Dict(
            {"camera": spaces.Box(low=0, high=255, shape=[3, camera.height, camera.width], dtype=np.uint8)}
        )

        for scene in self.scenes:
            scene.show(return_frames=False, return_nodes=False)

        VecEnv.__init__(self, len(self.scenes) * len(agents), self.observation_space, self.action_space)

        self.keys, shapes, dtypes = obs_space_info(self.observation_space)
        self.buf_obs = OrderedDict(
            [(k, np.zeros((self.num_envs,) + tuple(shapes[k]), dtype=dtypes[k])) for k in self.keys]
        )
        self.buf_rews = np.zeros((self.num_envs,), dtype=np.float32)
        self.buf_dones = np.zeros((self.num_envs,), dtype=bool)
        self.buf_infos = [{} for _ in range(self.num_envs)]
        self.actions = None

    def step_async(self, actions: np.ndarray):
        self.actions = actions

    def step_wait(self):
        scene_offset = 0
        for scene in self.scenes:
            agents = scene.agents
            action_dict = {}
            for i, action in enumerate(self.actions[scene_offset : scene_offset + len(agents)]):
                action_dict[agents[i].name] = int(action)
            event = scene.step(action=action_dict)
            for i, agent in enumerate(agents):
                agent_data = event["agents"][agent.name]
                self.buf_rews[scene_offset + i] = agent_data["reward"]
                self.buf_dones[scene_offset + i] = agent_data["done"]
                self.buf_infos[scene_offset + i] = {}
                camera = agent.rl_component.camera_sensors[0].camera
                obs = {"camera": np.array(agent_data["frames"][camera.name], dtype=np.uint8)}
                self._save_obs(scene_offset + i, obs)
            scene_offset += len(agents)
        return (self._obs_from_buf(), np.copy(self.buf_rews), np.copy(self.buf_dones), deepcopy(self.buf_infos))

    def reset(self):
        scene_offset = 0
        for scene in self.scenes:
            agents = scene.agents
            scene.reset()
            event = scene.step(return_frames=True, frame_skip=0)
            for i, agent in enumerate(agents):
                camera = agent.rl_component.camera_sensors[0].camera
                obs = {"camera": np.array(event["frames"][camera.name], dtype=np.uint8)}
                self._save_obs(scene_offset + i, obs)
            scene_offset += len(agents)
        return self._obs_from_buf()

    def close(self):
        self.scene.close()

    def _save_obs(self, index: int, obs: VecEnvObs):
        for key in self.keys:
            if key is None:
                self.buf_obs[key][index] = obs
            else:
                self.buf_obs[key][index] = obs[key]

    def _obs_from_buf(self) -> VecEnvObs:
        return dict_to_obs(self.observation_space, copy_obs_dict(self.buf_obs))

    def env_is_wrapped(self):
        return False

    def seed(self, seed):
        raise NotImplementedError()

    def env_method(self):
        raise NotImplementedError()

    def set_attr(self):
        raise NotImplementedError()

    def get_attr(self):
        raise NotImplementedError()
