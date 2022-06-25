from dataclasses import dataclass
from typing import Optional

from ..asset import Asset


@dataclass
class RlAgentRewardFunction:
    function: Optional[str] = "dense"
    entity1: Optional[Asset] = None
    entity2: Optional[Asset] = None
    distance_metric: Optional[str] = "euclidean"
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False

    def _post_copy(self, agent):
        root = agent.tree_root

        new_instance = type(self)(
            function=self.function,
            entity1=root.get(self.entity1._get_last_copy_name()),
            entity2=root.get(self.entity2._get_last_copy_name()),
            distance_metric=self.distance_metric,
            scalar=self.scalar,
            threshold=self.threshold,
            is_terminal=self.is_terminal,
        )

        return new_instance
