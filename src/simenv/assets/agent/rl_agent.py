import itertools
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from simenv.gltflib.models import camera

from ..asset import Asset
from .rl_agent_actions import DiscreteRLAgentActions, RLAgentActions
from .rl_agent_reward_function import RLAgentRewardFunction


class RLAgent(Asset):
    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        color: Optional[List[float]] = None,
        height: Optional[float] = 1.5,
        move_speed: Optional[float] = 5.0,
        turn_speed: Optional[float] = 2.0,
        actions: Optional[RLAgentActions] = None,
        reward_functions: Optional[List[RLAgentRewardFunction]] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        camera_width=32,
        camera_height=32,
        parent: Optional[Asset] = None,
        children: Optional[List[Asset]] = None,
    ):
        super().__init__(name=name, position=position, rotation=rotation, parent=parent, children=children)

        if color is None:
            color = [1.0, 0.0, 0.0]
        if actions is None:
            actions = DiscreteRLAgentActions.default()
        if reward_functions is None:
            reward_functions = []

        self.color = color
        self.height = height
        self.move_speed = move_speed
        self.turn_speed = turn_speed
        self.actions = actions
        self.camera_height = camera_height
        self.camera_width = camera_width
        self.reward_functions = reward_functions

    def add_reward_function(self, reward_function: RLAgentRewardFunction) -> None:
        self.reward_functions.append(reward_function)
