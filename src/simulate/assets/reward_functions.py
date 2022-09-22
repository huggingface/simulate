import itertools
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, List, Optional, Union

from .asset import Asset
from .gltf_extension import GltfExtensionMixin


ALLOWED_REWARD_TYPES = ["dense", "sparse", "or", "and", "not", "see", "timeout", "angle_to"]
ALLOWED_REWARD_DISTANCE_METRICS = ["euclidean"]  # TODO(Ed) other metrics?


@dataclass
class RewardFunction(Asset, GltfExtensionMixin, gltf_extension_name="HF_reward_functions", object_type="node"):
    """An RL reward function

    Attributes:
        type: str, optional (default="dense")
            The type of reward function. Must be one of the following:
                "dense", "sparse", "or", "and", "not", "see", "timeout"
        distance_metric: str, optional (default="euclidean")
            The distance metric to use. Must be one of the following:
                "euclidean"
        entity_a: Asset
            The first entity in the reward function
        entity_b: Asset
            The second entity in the reward function
        scalar: float, optional (default=1.0)
            The scalar to modify the reward by a constant. Setting to -1 will make the reward behave as a cost.
        threshold: float, optional (default=0.0)
            The distance threshold to give the reward
        is_terminal: bool, optional (default=False)
            Whether the reward is terminal
        is_collectable: bool, optional (default=False)
            Whether the reward is collectable
        trigger_once: bool, optional (default=False)
            Whether the reward is triggered once
        reward_function_a: RewardFunction, optional (default=None)
            When doing combination of rewards (and, or), the first reward function that are to be combined
        reward_function_b: RewardFunction, optional (default=None)
            When doing combination of rewards (and, or), the second reward function that are to be combined
    """

    type: Optional[str] = None
    entity_a: Optional[Any] = None
    entity_b: Optional[Any] = None
    distance_metric: Optional[str] = None
    direction: Optional[List[float]] = None
    scalar: Optional[float] = 1.0
    threshold: Optional[float] = 1.0
    is_terminal: Optional[bool] = False
    is_collectable: Optional[bool] = False
    trigger_once: Optional[bool] = True
    reward_function_a: InitVar[Optional["RewardFunction"]] = None  # There are in the tree structure now
    reward_function_b: InitVar[Optional["RewardFunction"]] = None

    name: InitVar[Optional[str]] = None
    position: InitVar[Optional[List[float]]] = None
    rotation: InitVar[Optional[List[float]]] = None
    scaling: InitVar[Optional[Union[float, List[float]]]] = None
    transformation_matrix: InitVar[Optional[List[float]]] = None
    parent: InitVar[Optional[Any]] = None
    children: InitVar[Optional[List[Any]]] = None
    created_from_file: InitVar[Optional[str]] = None

    __NEW_ID: ClassVar[Any] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __post_init__(
        self,
        reward_function_a,
        reward_function_b,
        name,
        position,
        rotation,
        scaling,
        transformation_matrix,
        parent,
        children,
        created_from_file,
    ):
        if reward_function_a is not None:
            children = (children if children else []) + reward_function_a
        if reward_function_b is not None:
            children = (children if children else []) + reward_function_b

        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            transformation_matrix=transformation_matrix,
            parent=parent,
            children=children,
            created_from_file=created_from_file,
        )

        if self.type is None:
            self.type = "dense"
        if self.type not in ALLOWED_REWARD_TYPES:
            raise ValueError(f"Invalid reward type: {self.type}. Must be one of: {ALLOWED_REWARD_TYPES}")
        if self.distance_metric is None:
            self.distance_metric = "euclidean"
        if self.distance_metric not in ALLOWED_REWARD_DISTANCE_METRICS:
            raise ValueError(
                f"Invalid distance metric: {self.distance_metric}. Must be one of: {ALLOWED_REWARD_DISTANCE_METRICS}"
            )
        if self.direction is None:
            self.direction = [1.0, 0.0, 0.0]

    def _post_attach_children(self, children):
        """Method call after attaching `children`.
        We only allow Reward Functions as child of Reward functions.
        """
        if children is not None:
            if any(not isinstance(child, "RewardFunction") for child in children):
                raise TypeError("The children of a Reward Function should be Reward Functions")

    def _post_copy(self, actor: Any):
        root = actor.tree_root

        copy_name = self.name + f"_copy{self._n_copies}"
        self._n_copies += 1

        new_instance = type(self)(
            name=copy_name,
            type=self.type,
            entity_a=root.get_node(self.entity_a._get_last_copy_name()),
            entity_b=root.get_node(self.entity_b._get_last_copy_name()),
            distance_metric=self.distance_metric,
            scalar=self.scalar,
            threshold=self.threshold,
            is_terminal=self.is_terminal,
            is_collectable=self.is_collectable,
            trigger_once=self.trigger_once,
            reward_function_a=self.tree_children[0] if self.tree_children else None,
            reward_function_b=self.tree_children[1] if self.tree_children and len(self.tree_children) > 1 else None,
        )

        return new_instance
