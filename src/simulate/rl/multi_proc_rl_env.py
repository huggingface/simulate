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
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Type, Union

import numpy as np


try:
    import gym
except ImportError:

    class gym:
        class Wrapper:
            pass


try:
    from stable_baselines3.common.vec_env.base_vec_env import VecEnv, VecEnvIndices
except ImportError:

    class VecEnv:
        pass  # Dummy class if SB3 is not installed

    class VecEnvIndices:
        pass  # Dummy class if SB3 is not installed


class MultiProcessRLEnv(VecEnv):
    """
    Multi-process RL environment wrapper for Simulate scene. Spawns multiple backend executables to run in parallel,
        in addition to the optionality of multiple maps.
    Uses functionality from the VecEnv in stable baselines 3. For more information on VecEnv, see the source
    https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html

    Args:
        env_fn (`Callable`): a generator function that returns a RLEnv / ParallelRLEnv for generating instances
            of the desired environment.
        n_parallel (`int`): the number of executable instances to create.
        starting_port (`int`): initial communication port for spawned executables.
    """

    def __init__(self, env_fn: Callable, n_parallel: int, starting_port: int = 55001):
        self.n_parallel = n_parallel
        self.envs = []
        observation_space = None
        action_space = None

        # create the environments
        for i in range(n_parallel):
            env = env_fn(starting_port + i)
            self.n_show = env.n_show
            observation_space = env.observation_space
            action_space = env.action_space
            self.envs.append(env)

        num_envs = self.n_show * self.n_parallel
        super().__init__(num_envs, observation_space, action_space)

    def step(self, actions: Optional[Union[list, np.array]] = None) -> Tuple[Dict, np.ndarray, np.ndarray, List[Dict]]:
        """
        The step function for the environment, follows the API from OpenAI Gym.

        Args:
            actions (`Dict` or `List`): TODO verify, a dict with actuator tags as keys and as values a Tensor of shape (n_show, n_actors, n_actions)

        Returns:
            all_observation (`Dict`): TODO
            all_reward (`float`): TODO
            all_done (`bool`): TODO
            all_info: TODO
        """
        if isinstance(actions, list):
            actions = np.array(actions)

        for i in range(self.n_parallel):
            # TODO comment what is going on here
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
        np_out = defaultdict(np.ndarray)

        for o in obs:
            for key, value in o.items():
                out[key].append(value)

        for key in out.keys():
            np_out[key] = np.concatenate(out[key], axis=0)

        return np_out

    def reset(self):
        # we aren't performing this async as this happens rarely as the env auto resets
        all_obs = []
        for i in range(self.n_parallel):
            obs = self.envs[i].reset()
            all_obs.append(obs)
        all_obs = self._combine_obs(all_obs)

        return all_obs

    def close(self):
        for env in self.envs:
            env.scene.close()

    def env_is_wrapped(self, wrapper_class: Type[gym.Wrapper], indices: VecEnvIndices = None) -> List[bool]:
        return [False] * self.n_show * self.n_parallel

    # required abstract methods

    def step_async(self, actions: np.ndarray) -> None:
        raise NotImplementedError()

    def seed(self, seed: Optional[int] = None):  # -> List[Union[None, int]]:
        # this should be done when the env is initialized
        return
        # raise NotImplementedError()

    def get_attr(self, attr_name: str, indices: VecEnvIndices = None) -> List[Any]:
        raise NotImplementedError()

    def set_attr(self, attr_name: str, value: Any, indices: VecEnvIndices = None) -> None:
        raise NotImplementedError()

    def env_method(self, method_name: str, *method_args, indices: VecEnvIndices = None, **method_kwargs) -> List[Any]:
        raise NotImplementedError()

    def get_images(self) -> Sequence[np.ndarray]:
        raise NotImplementedError()

    def step_send(self):
        raise NotImplementedError()

    def step_wait(self):
        raise NotImplementedError()
