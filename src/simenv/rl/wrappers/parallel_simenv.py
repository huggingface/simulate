import numpy as np
from stable_baselines3.common.vec_env.base_vec_env import VecEnv


class ParallelSimEnv(VecEnv):
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

        #self.auto_reset(dones) this is not handled on the unity size
        obs = self._get_observations()
        return obs, rewards, dones, [{}] * self.n_parallel * self.n_agents

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

    def _get_observations(self):
        for i in range(self.n_parallel):
            self.envs[i].engine.get_observation_send()

        # receive the acks
        obss = []
        for i in range(self.n_parallel):
            obs = self.envs[i].engine.get_observation_recv()
            obss.append(obs)

        obss = np.concatenate(obss, 0)

        return obss

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
