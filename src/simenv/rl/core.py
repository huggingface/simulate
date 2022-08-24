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
""" An RL component."""
from dataclasses import dataclass
from typing import List, Optional, Union

import numpy as np

from ..assets import Asset, CameraSensor, Collider, GltfExtensionMixin, RaycastSensor, StateSensor
from .actions import BoxAction, DiscreteAction
from .reward_functions import RewardFunction


class Agent(Asset):
    """
    Base class for agent API in SimEnv.
    """

    def __init__(
        self,
        name=None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        collider: Optional[Collider] = None,
        transformation_matrix=None,
        parent=None,
        children=None,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            collider=collider,
            transformation_matrix=transformation_matrix,
        )
        # self.reward_function = None
        # self.action_space = None
        # self.state_space = None

    def act(self, obs: np.ndarray, **_kwargs) -> np.ndarray:
        """
        Takes in an observation and returns an action.
        """
        pass

    def reset(self):
        """Resets any internal state of the agent."""
        pass

    def copy(self, with_children=True, **kwargs) -> "Agent":
        """Return a copy of the Asset. Parent and children are not attached to the copy."""

        copy_name = self.name + f"_copy{self._n_copies}"
        self._n_copies += 1
        instance_copy = type(self)(
            name=copy_name,
            position=self.position,
            rotation=self.rotation,
            scaling=self.scaling,
            collider=self.collider,
        )

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children

            for child in instance_copy.tree_children:
                child._post_copy()

        instance_copy.rl_component = RlComponent(
            self.rl_component.actions, self.rl_component.sensors, self.rl_component.rewards
        )

        instance_copy.physics_component = self.physics_component

        return instance_copy

    def _post_copy(self):
        self.rl_component._post_copy(self)

    def add_reward_function(self, reward_function: RewardFunction):
        if self.rl_component.reward_functions is None:
            self.rl_component.reward_functions = []
        self.rl_component.reward_functions.append(reward_function)


@dataclass
class RlComponent(GltfExtensionMixin, gltf_extension_name="HF_rl_agents"):
    """A reinforcement learning component to make an RL Agent from an Asset.

    Store:
    - actions: action space as a gym.space mapped to the physics engine variables
    - observations: observation devices as assets (e.g. cameras)
    - rewards: reward functions
    """

    box_actions: Optional[BoxAction] = None
    discrete_actions: Optional[DiscreteAction] = None
    camera_sensors: Optional[List[CameraSensor]] = None
    state_sensors: Optional[List[StateSensor]] = None
    raycast_sensors: Optional[List[RaycastSensor]] = None
    reward_functions: Optional[List[RewardFunction]] = None

    def __post_init__(self):
        if self.camera_sensors is not None and not isinstance(self.camera_sensors, list):
            self.camera_sensors = [self.camera_sensors]
        if self.state_sensors is not None and not isinstance(self.state_sensors, list):
            self.state_sensors = [self.state_sensors]
        if self.raycast_sensors is not None and not isinstance(self.raycast_sensors, list):
            self.raycast_sensors = [self.raycast_sensors]
        if self.reward_functions is not None and not isinstance(self.reward_functions, list):
            self.reward_functions = [self.reward_functions]

    def _post_copy(self, agent: "Asset"):
        self.reward_functions = [rf._post_copy(agent) for rf in self.reward_functions]

        root = agent.tree_root
        updated_sensors = []
        for obs in self.sensors:
            updated_obs = root.get_node(obs._get_last_copy_name())
            updated_sensors.append(updated_obs)

        self.sensors = updated_sensors
