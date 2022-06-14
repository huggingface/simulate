from dataclasses import dataclass
from typing import Optional


@dataclass
class RLAgentRewardFunction:
    function: Optional[str] = "dense"
    entity1: Optional[str] = "agent"
    entity2: Optional[str] = None
    distance_metric: Optional[str] = "euclidean"
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False
