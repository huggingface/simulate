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
from typing import List, Optional, Union, TYPE_CHECKING

from .actions import MappedBox, MappedDiscrete
from .observations import map_observation_devices_to_spaces
from .rewards import RewardFunction

if TYPE_CHECKING:
    from ..assets import Asset

try:
    from gym import spaces
except ImportError:
    raise


class RlComponent:
    """A reinforcement learning component to make an RL Agent from an Asset.

    Store:
    - actions: action space as a gym.space mapped to the physics engine variables
    - observations: observation devices as assets (e.g. cameras)
    - rewards: reward functions
    """

    def __init__(
        self,
        actions: Union[MappedBox, MappedDiscrete] = None,
        observations: Optional[Union["Asset", List["Asset"]]] = None,
        rewards: Optional[Union[RewardFunction, List[RewardFunction]]] = None,
    ):
        # Action space mapped to physics engine variables
        self.actions = actions

        # Observation devices as Assets
        if observations is None:
            observations = []
        elif not isinstance(observations, (list, tuple)):
            observations = [observations]
        self.observations = observations
        self.observation_space = [map_observation_devices_to_spaces(device) for device in observations]

        # Reward functions
        if rewards is None:
            rewards = []
        elif not isinstance(rewards, (list, tuple)):
            rewards = [rewards]
        self.rewards = rewards

    @property
    def action_space(self):
        return self.actions

    def copy(self):
        instance_copy = type(self)(
            actions=self.actions,
            observations=self.observations,
            rewards=self.rewards,
        )
        return instance_copy

    def _post_copy(self):
        self.rewards = [rf._post_copy(self) for rf in self.rewards]
        # TODO handle observation devices as well

    def __repr__(self):
        return f"RlComponent(actions={self.actions}, observations={self.observations}, rewards={self.rewards})"
