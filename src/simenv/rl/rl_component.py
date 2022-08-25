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
from typing import TYPE_CHECKING, List, Optional

import numpy as np
from gym import spaces

from ..assets.gltf_extension import GltfExtensionMixin
from ..assets.sensors import CameraSensor, RaycastSensor, StateSensor
from .actions import BoxAction, DiscreteAction
from .reward_functions import RewardFunction


if TYPE_CHECKING:
    from ..assets import Asset


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

        # if not isinstance(self.sensors, (list, tuple)):
        #     self.sensors = [self.sensors]
        # # Action space mapped to physics engine variables
        # self.actions = actions

        # # Observation devices as Assets
        # if sensors is None:
        #     sensors = []
        # elif not isinstance(sensors, (list, tuple)):
        #     sensors = [sensors]
        # self.sensors = sensors
        # TODO: to be compatable with StableBaselines3, a list of observations spaces should be a spaces.Tuple
        # or spaces.Dict observation space. This requires a refactor that will be in its own PR.

        # self.observation_space = spaces.Dict(
        #     {type(sensor).__name__: map_sensors_to_spaces(sensor) for sensor in self.camera_sensors}  # FIXME
        # )

        # # Reward functions
        # if rewards is None:
        #     rewards = []
        # elif not isinstance(rewards, (list, tuple)):
        #     rewards = [rewards]
        # self.rewards = rewards

    @property
    def action_space(self):
        if self.discrete_actions is not None:
            return self.discrete_actions
        if self.box_actions is not None:
            return self.box_actions
        raise NotImplementedError("Action space not found/implemented")

    @property
    def observation_space(self):
        if self.camera_sensors is not None and len(self.camera_sensors) > 0:
            camera = self.camera_sensors[0]
            space = spaces.Box(low=0, high=255, shape=(3, camera.camera.height, camera.camera.width), dtype=np.uint8)
            return space
        raise NotImplementedError("Sensors not found/implemented")

    def _post_copy(self, agent: "Asset"):
        self.reward_functions = [rf._post_copy(agent) for rf in self.reward_functions]

        root = agent.tree_root
        updated_sensors = []
        for obs in self.sensors:
            updated_obs = root.get_node(obs._get_last_copy_name())
            updated_sensors.append(updated_obs)

        self.sensors = updated_sensors
