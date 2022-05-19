import itertools
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from ..asset import Asset
from .rl_agent_actions import DiscreteRLAgentActions


class RL_Agent(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name,
        color=[1.0, 0.0, 0.0],
        height=1.5,
        move_speed=2.0,
        turn_speed=2.0,
        actions=DiscreteRLAgentActions.default(),
        translation=[0, 0, 0],
        rotation=[0, 0, 0, 1],
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, translation=translation, rotation=rotation, parent=parent, children=children)

        self.color = color
        self.height = height
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.actions = actions
