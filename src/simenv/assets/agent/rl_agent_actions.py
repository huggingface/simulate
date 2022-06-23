from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RLAgentActions:
    name: Optional[str] = None
    dist: Optional[str] = None
    available_actions: Optional[List[str]] = None


class DiscreteRLAgentActions(RLAgentActions):
    def __init__(self, name=None, dist=None, available_actions=None) -> None:
        super().__init__(name=name, dist=dist, available_actions=available_actions)

    @classmethod
    def default(cls):
        return cls(
            name="movement",
            dist="discrete",
            available_actions=["move_forward", "move_backward", "move_left", "move_right", "turn_left", "turn_right"],
        )


class ContinuousRLAgentActions(RLAgentActions):
    def __init__(self, name=None, dist=None, types=None, available_actions=None) -> None:
        super().__init__(name=name, dist=dist, types=types, available_actions=available_actions)

    @classmethod
    def default(cls):
        return cls(
            name="movement",
            dist="continuous",
            available_actions=["move_forward_backward", "move_right_left", "turn_right_left"],
        )
