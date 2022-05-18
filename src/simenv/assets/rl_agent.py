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
""" A simenv RL Agent."""
import itertools
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from ..rl import DiscreteRLAgentActions, RLAgentActions
from .asset import Asset


class RLAgent(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        color: Optional[List[float]] = None,
        height: Optional[float] = 1.5,
        move_speed: Optional[float] = 2.0,
        turn_speed: Optional[float] = 0.4,
        actions: Optional[RLAgentActions] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, position=position, rotation=rotation, parent=parent, children=children)

        if color is None:
            color = [1.0, 0.0, 0.0]
        if actions is None:
            actions = DiscreteRLAgentActions.default()
        self.color = color
        self.height = height
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.actions = actions
