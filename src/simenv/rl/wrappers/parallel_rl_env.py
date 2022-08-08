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
""" A parallel env wrapper for Stable Baseline 3 mostly but also more general."""
import numpy as np


try:
    from stable_baselines3.common.vec_env.base_vec_env import VecEnv
except ImportError:

    class VecEnv:
        pass  # Dummy class if SB3 is not installed


class ParallelRLEnvironment(VecEnv):
    # Launched several env processes and communicates with
    # them in a semi-async manner

    def __init__(self, env_fn, n_parallel: int, starting_port=55000):
        self.n_parallel = n_parallel
        self.envs = []
        # create the environments
        for i in range(n_parallel):
            env = env_fn(starting_port + i)
            self.n_agents = env.n_agents
            num_envs = self.n_agents * self.n_parallel

            observation_space = env.observation_space
            action_space = env.action_space

            self.envs.append(env)
        super().__init__(num_envs, observation_space, action_space)

    #
    def reset(self):
        return self._reset()
        # get obs

    def _reset(self):
        for i in range(self.n_parallel):
            self.envs[i].engine.reset_send()

        for i in range(self.n_parallel):
            self.envs[i].engine.reset_recv()

        return self._get_observations()

    def step(self, actions):
        self._step(actions)
        # must return obs, reward, done, info
        dones = self._get_done()
        rewards = self._get_rewards()

        # self.auto_reset(dones) this is now handled on the unity size
        obs = self._get_observations()
        info = [{}] * self.n_parallel * self.n_agents
        return obs, rewards, dones, info

    def auto_reset(self, dones):
        # need to reset if done
        for i in range(self.n_parallel):
            if dones[i]:
                self.envs[i].engine.reset_send()

        for i in range(self.n_parallel):
            if dones[i]:
                self.envs[i].engine.reset_recv()

    def _step(self, actions):
        # unpack and send the actions
        for i in range(self.n_parallel):
            action = actions[i * self.n_agents : (i + 1) * self.n_agents]
            self.envs[i].engine.step_send(action.tolist())

        # receive the acks
        for i in range(self.n_parallel):
            self.envs[i].engine.step_recv()

    def _get_rewards(self):
        for i in range(self.n_parallel):
            self.envs[i].engine.get_reward_send()

        # receive the acks
        rewards = []
        for i in range(self.n_parallel):
            reward = self.envs[i].engine.get_reward_recv()
            rewards.extend(reward)

        return rewards

    def _get_done(self):
        for i in range(self.n_parallel):
            self.envs[i].engine.get_done_send()

        # receive the acks
        dones = []
        for i in range(self.n_parallel):
            done = self.envs[i].engine.get_done_recv()
            dones.extend(done)

        return np.array(dones)

    def close(self):
        for i in range(self.n_parallel):
            self.envs[i].engine.close()

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
