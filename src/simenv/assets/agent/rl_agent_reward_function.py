from dataclasses import dataclass
from typing import Optional

from simenv.assets import Asset


@dataclass
class RLAgentRewardFunction:
    function: Optional[str] = "dense"
    entity1: Optional[Asset] = None
    entity2: Optional[Asset] = None
    distance_metric: Optional[str] = "euclidean"
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False
