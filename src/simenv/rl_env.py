import gym
import numpy as np
from gym import spaces

from simenv.assets import agent


class RLEnv(gym.Env):
    def __init__(self, scene) -> None:
        super().__init__()

        self.scene = scene
        self.agents = scene.get_agents()
        assert len(self.agents), "at least one sm.Agent is require in the scene for RL"

        agent_actions: agent.RLAgentActions = self.agents[0].actions

        if agent_actions.dist == "discrete":
            n_actions = len(agent_actions.available_actions)
            self.action_space = spaces.Discrete(n_actions)
        else:
            self.action_space = spaces.Box(low=-1, high=1, shape=[len(agent_actions.types)])

        camera_width = self.agents[0].camera.width
        camera_height = self.agents[0].camera.height

        self.observation_space = spaces.Box(low=0, high=255, shape=[camera_height, camera_width, 3])

    def reset(self):
        self.scene.reset()
        obs = self.scene.get_observation()
        # TODO: remove np.flip for training (the agent does not care the world is upside-down
        obs = np.flip(np.array(obs["Items"]).reshape(*self.observation_space.shape), 0)

        return obs

    def step(self, action):
        self.scene.step(action)

        obs = self.scene.get_observation()
        # TODO: remove np.flip for training (the agent does not care the world is upside-down
        obs = np.flip(np.array(obs["Items"]).reshape(*self.observation_space.shape), 0)

        reward = self.scene.get_reward()
        done = self.scene.get_done()
        info = {}  # TODO: Add info to the backend, if we require it

        return obs, reward, done, info

    def close(self):
        self.scene.close()
