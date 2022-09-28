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

from collections import defaultdict
from typing import Optional

import numpy as np


try:
    from stable_baselines3.common.vec_env.base_vec_env import VecEnv
except ImportError:

    class VecEnv:
        pass  # Dummy class if SB3 is not installed


class ParallelRLEnv(VecEnv):
    """
    Parallel RL environment wrapper for Simulate scene. Spawns multiple backend executables to run in parallel, in addition to the optionality of multiple maps.
    Uses functionality from the VecEnv in stable baselines 3. For more information on VecEnv, see the source
    https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html

    Args:
        env_fn: a generator function for generating instances of the desired environment
        n_maps: the number of map instances to create, default 1
        n_show: optionally show a subset of the maps during training and dequeue a new map at the end of each episode
        time_step: the physics timestep of the environment
        frame_skip: the number of times an action is repeated before the next observation is returned
    """

    def __init__(self, env_fn, n_parallel: int, starting_port: int = 55000):
        self.n_parallel = n_parallel
        self.envs = []
        # create the environments
        for i in range(n_parallel):
            env = env_fn(starting_port + i)
            self.n_show = env.n_show

            observation_space = env.observation_space
            action_space = env.action_space

            self.envs.append(env)
        num_envs = self.n_show * self.n_parallel
        super().__init__(num_envs, observation_space, action_space)

    def step(self, actions: Optional[np.array] = None):
        for i in range(self.n_parallel):
            action = actions[i * self.n_show : (i + 1) * self.n_show] if actions is not None else None
            self.envs[i].step_send_async(action)

        all_obs = []
        all_reward = []
        all_done = []
        all_info = []

        for i in range(self.n_parallel):
            obs, reward, done, info = self.envs[i].step_recv_async()

            all_obs.append(obs)
            all_reward.extend(reward)
            all_done.extend(done)
            all_info.extend(info)

        all_obs = self._combine_obs(all_obs)
        all_reward = np.array(all_reward)
        all_done = np.array(all_done)

        return all_obs, all_reward, all_done, all_info

    @staticmethod
    def _combine_obs(obs):
        out = defaultdict(list)

        for o in obs:
            for key, value in o.items():
                out[key].append(value)

        for key in out.keys():
            out[key] = np.concatenate(out[key], axis=0)

        return out

    def reset(self):
        # we aren't performing this async as this happens rarely as the env auto resets
        all_obs = []
        for i in range(self.n_parallel):
            obs = self.envs[i].reset()
            all_obs.append(obs)
        all_obs = self._combine_obs(all_obs)

        return all_obs

    def close(self):
        self.scene.close()

    def env_is_wrapped(self):
        return [False] * self.n_show * self.n_parallel

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
