import gym
import numpy as np
from gym import spaces

from .assets import agent
from .scene import Scene


class RLEnv(gym.Env):
    def __init__(self, scene: Scene) -> None:
        super().__init__()

        self.scene = scene
        self.agents = scene.agents
        self.n_agents = len(self.agents)

        assert len(self.agents), "at least one sm.Agent is require in the scene for RL"

        agent_actions: agent.RLAgentActions = self.agents[0].actions

        if agent_actions.dist == "discrete":
            n_actions = len(agent_actions.available_actions)
            self.action_space = spaces.Discrete(n_actions)
        else:
            self.action_space = spaces.Box(low=-1, high=1, shape=[len(agent_actions.types)])

        self.camera_width = self.agents[0].camera.width
        self.camera_height = self.agents[0].camera.height

        self.observation_space = spaces.Box(
            low=0, high=255, shape=[3, self.camera_height, self.camera_width], dtype=np.uint8
        )

    def reset(self):
        self.scene.reset()
        obs = self.scene.get_observation()

        obs = self._reshape_obs(obs)

        return obs

    def _reshape_obs(self, obs):
        # TODO: remove np.flip for training (the agent does not care the world is upside-down
        # TODO: have unity side send in B,C,H,W order
        return np.flip(
            np.array(obs["Items"]).astype(np.uint8).reshape(self.n_agents, self.camera_height, self.camera_width, 3), 1
        ).transpose(0, 3, 1, 2)

    def step(self, action):
        self.scene.step(action)

        obs = self.scene.get_observation()
        # TODO: remove np.flip for training (the agent does not care the world is upside-down
        obs = self._reshape_obs(obs)

        reward = self.scene.get_reward()
        done = self.scene.get_done()
        info = {}  # TODO: Add info to the backend, if we require it

        return obs, reward, done, info

    def close(self):
        self.scene.close()

    # async sim interaction

    def step_send(self, action):
        return self.scene.engine.step_send(action.tolist())

    def step_recv(self):
        return self.scene.engine.step_recv()

    def get_reward_send(self):
        return self.scene.engine.get_reward_send()

    def get_reward_recv(self):
        return self.scene.engine.get_reward_recv()

    def get_done_send(self):
        return self.scene.engine.get_done_send()

    def get_done_recv(self):
        return self.scene.engine.get_done_recv()

    def reset_send(self):
        return self.scene.engine.reset_send()

    def reset_recv(self):
        return self.scene.engine.reset_recv()

    def get_observation_send(self):
        return self.scene.engine.get_observation_send()

    def get_observation_recv(self):
        return self._reshape_obs(self.scene.engine.get_observation_recv())
