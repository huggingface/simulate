from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from ..assets import Asset


ALLOWED_REWARD_TYPES = ["dense", "sparse"]
ALLOWER_REWARD_DISTANCE_METRICS = ["euclidean"]  # TODO(Ed) other metrics?


@dataclass
class RewardFunction:
    """An RL reward function"""

    entity_a: "Asset"
    entity_b: "Asset"
    type: Optional[str] = None
    distance_metric: Optional[str] = None
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False

    def __post_init__(self):
        if self.type is None:
            self.type = "dense"
        if self.distance_metric is None:
            self.distance_metric = "euclidean"

    def _post_copy(self, agent: "Asset"):
        root = agent.tree_root

        new_instance = type(self)(
            type=self.type,
            entity_a=root.get(self.entity_a._get_last_copy_name()),
            entity_b=root.get(self.entity_b._get_last_copy_name()),
            distance_metric=self.distance_metric,
            scalar=self.scalar,
            threshold=self.threshold,
            is_terminal=self.is_terminal,
        )

        return new_instance
