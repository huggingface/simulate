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
"""Wrapper around SimEnv scene for easier RL training"""

import gym
import numpy as np
from gym import spaces

# Lint as: python3
from ...scene import Scene


class RLEnvironment(gym.Env):
    def __init__(self, scene: Scene):
        super(RLEnvironment, self).__init__()
        self.scene = scene

        agents = scene.agents
        if len(agents) == 0:
            print("No agent found. Add at least one agent to the scene")
            return
        elif len(agents) > 1:
            print("More than one agent not supported. Use ParallelEnvironment for multiple agents per scene")
        self.agent = agents[0]

        self.action_space = None
        if self.agent.rl_component.discrete_actions is not None:
            self.action_space = self.agent.rl_component.discrete_actions
        elif self.agent.rl_component.box_actions is not None:
            self.action_space = self.agent.rl_component.box_actions
        if self.action_space is None:
            print("Action space not found. Does the environment contain an agent with an action space?")

        self.observation_space = {}
        if self.agent.rl_component.camera_sensors is not None and len(self.agent.rl_component.camera_sensors) > 0:
            camera = self.agent.rl_component.camera_sensors[0].camera
            self.observation_space[camera.name] = spaces.Box(
                low=0, high=255, shape=[3, camera.height, camera.width], dtype=np.uint8
            )
        if len(self.observation_space) > 0:
            self.observation_space = spaces.Dict(self.observation_space)
        else:
            print("Observation space not found. Does the environment contain an agent with a valid sensor?")

        # Don't return simulation data, since minimal/faster data will be returned by agent sensors
        self.scene.show(return_frames=False, return_nodes=False)

    def step(self, action):
        event = self.scene.step(action={self.agent.name: int(action)})

        # Extract observations, reward, and done from event data
        obs = {}
        reward = 0.0
        done = False
        info = {}
        try:
            agent_data = event["agents"][self.agent.name]
            camera = self.agent.rl_component.camera_sensors[0].camera
            obs[camera.name] = np.array(agent_data["frames"][camera.name], dtype=np.uint8)
            reward = agent_data["reward"]
            done = agent_data["done"]
        except Exception:
            print("Failed to parse agent data from event: " + str(event))

        return obs, reward, done, info

    def reset(self):
        self.scene.reset()

        # To extract observations, we do a "fake" step (no actual simulation with frame_skip=0)
        event = self.scene.step(return_frames=True, frame_skip=0)
        obs = {}
        try:
            camera = self.agent.rl_component.camera_sensors[0].camera
            obs[camera.name] = np.array(event["frames"][camera.name], dtype=np.uint8)
        except Exception:
            print("Failed to get observations from event: " + str(event))
            pass

        return obs

    def close(self):
        self.scene.close()
