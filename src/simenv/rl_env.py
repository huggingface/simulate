import gym
from gym import spaces
from simenv.assets import agent
import numpy as np

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

        camera_width =self.agents[0].camera_width
        camera_height =self.agents[0].camera_height

        self.observation_space = spaces.Box(low=0, high=255, shape=[camera_height, camera_width, 3])

    def reset(self):
        raise NotImplementedError

    def step(self, action):
        self.scene.step(action)

        obs = self.scene.get_observation()
        # TODO: remove np.flip for training (the agent does not care the world is upside-down
        obs = np.flip(np.array(obs["Items"]).reshape(*self.observation_space.shape),0)
        # reward = scene.get_reward()
        # info = scene.get_info()

        return obs

