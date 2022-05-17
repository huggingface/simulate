import gym
from gym import spaces

import simenv as sm
from simenv.assets import agent


class RL_Env(gym.Env):
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

        self.observation_space = None  # TODO

    def reset(self):
        raise NotImplementedError

    def step(self, action):
        self.scene.step(action)

        # TODO: return observation
