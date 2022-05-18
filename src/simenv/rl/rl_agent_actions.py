from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np


@dataclass
class RLAgentActions:
    name: Optional[str] = field(default_factory=lambda: ["movement"])
    dist: Optional[str] = None
    available_actions: Optional[List[str]] = None


class DiscreteRLAgentActions(RLAgentActions):
    dist: Optional[str] = field(default_factory=lambda: ["discrete"])
    available_actions: Optional[List[str]] = field(default_factory=lambda: ["move_forward", "move_backward", "move_left", "move_right", "turn_left", "turn_right"])

class ContinuousRLAgentActions(RLAgentActions):
    dist: Optional[str] = field(default_factory=lambda: ["continuous"])
    available_actions: Optional[List[str]] = field(default_factory=lambda: ["move_forward_backward", "move_right_left", "turn_right_left"])
