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
import itertools
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, List, Optional, Tuple, Union

import numpy as np

from .asset import Asset, get_transform_from_trs, get_trs_from_transform_matrix, rotation_from_euler_degrees
from .gltf_extension import GltfExtensionMixin


ALLOWED_REWARD_TYPES = ["dense", "sparse", "or", "and", "not", "see", "timeout", "angle_to"]
ALLOWED_REWARD_DISTANCE_METRICS = ["euclidean", "best_euclidean", "cosine"]  # TODO: other metrics?


@dataclass
class RewardFunction(Asset, GltfExtensionMixin, gltf_extension_name="HF_reward_functions", object_type="node"):
    """
    A reinforcement learning reward function.

    Args:
        type (`str`, *optional*, defaults to `"dense"`):
            The type of reward function. Must be one of the following:
            [
                "dense",
                "sparse",
                "or",
                "and",
                "not",
                "see",
                "timeout"
            ]
        entity_a (`Asset`, *optional*, defaults to `None`):
            The first entity in the reward function
        entity_b: (`Asset`, *optional*, defaults to `None`):
            The second entity in the reward function
        distance_metric (`str`, *optional*, defaults to `"euclidean"`):
            The distance metric to use. Must be one of the following:
            [
                "euclidean"
            ]
        direction (List[float], *optional*, defaults to `[1.0, 0.0, 0.0]`):
            The direction to use for the reward function.
        scalar (`float`, *optional*, defaults to `1.0`):
            The scalar to modify the reward by a constant. Setting to -1 will make the reward behave as a cost.
        threshold (`float`, *optional*, defaults to `1.0`):
            The distance threshold to give the reward
        is_terminal (`bool`, *optional*, defaults to `False`):
            Whether the reward is terminal
        is_collectable (`bool`, *optional*, defaults to `False`):
            Whether the reward is collectable
        trigger_once (`bool`, *optional*, defaults to `True`):
            Whether the reward is triggered once
        reward_function_a (`RewardFunction`, *optional*, defaults to `None`):
            When doing combination of rewards (and, or), the first reward function that are to be combined
        reward_function_b (`RewardFunction`, *optional*, defaults to `None`):
            When doing combination of rewards (and, or), the second reward function that are to be combined

        name (`str`, *optional*, defaults to `None`):
            The name of the reward function
        position (List[float], *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The position of the reward function.
        rotation (List[float], *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The rotation of the reward function.
        scaling (List[float], *optional*, defaults to `[1.0, 1.0, 1.0]`):
            The scaling of the reward function.
        transformation_matrix (List[float], *optional*, defaults to `None`):
            The transformation matrix of the reward function.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the reward function.
        children (`List[Asset]`, *optional*, defaults to `None`):
            The children of the reward function.
        created_from_file (`str`, *optional*, defaults to `None`):
            The file path of the file from which the reward function was created.
    """

    type: Optional[str] = None
    entity_a: Optional[Any] = None
    entity_b: Optional[Any] = None
    distance_metric: Optional[str] = None
    direction: Optional[List[float]] = None
    scalar: float = 1.0
    threshold: float = 1.0
    is_terminal: bool = False
    is_collectable: bool = False
    trigger_once: bool = True
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
            children = (children if children else []) + [reward_function_a]
        if reward_function_b is not None:
            children = (children if children else []) + [reward_function_b]

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

    def _post_attach_children(self, children: Union["Asset", List["Asset"]]):
        """
        Method call after attaching `children`.
        We only allow Reward Functions as child of Reward functions.

        Args:
            children (`Union[Asset, List[Asset]]`):
                The children to attach.
        """
        if children is not None:
            if any(not isinstance(child, self.__class__) for child in children):
                raise TypeError("The children of a Reward Function should be Reward Functions")

    def _post_copy(self, actor: "Asset"):
        """
        Method call after copying the reward function.

        Args:
            actor (`Asset`):
                The actor used to access the root.
        """
        root = actor.tree_root

        copy_name = getattr(self, "name") + f"_copy{self._n_copies}"
        self._n_copies += 1

        new_instance = RewardFunction(
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

    ##############################
    # Properties copied from Asset()
    # We need to redefine them here otherwise the dataclass lose them since
    # they are also in the __init__ signature
    #
    # Need to be updated if Asset() is updated
    ##############################
    @property
    def position(self) -> Union[List[float], np.ndarray]:
        """
        Get the position of the reward function in the scene.

        Returns:
            position (`List[float]` or `np.ndarray`):
                The position of the reward function in the scene.
        """
        return self._position

    @property
    def rotation(self) -> Union[List[float], np.ndarray]:
        """
        Get the rotation of the reward function in the scene.

        Returns:
            rotation (`List[float]` or `np.ndarray`):
                The rotation of the reward function in the scene.
        """
        return self._rotation

    @property
    def scaling(self) -> Union[List[float], np.ndarray]:
        """
        Get the scaling of the reward function in the scene.

        Returns:
            scaling (`List[float]` or `np.ndarray`):
                The scaling of the reward function in the scene.
        """
        return self._scaling

    @property
    def transformation_matrix(self) -> np.ndarray:
        """
        Get the transformation matrix of the reward function in the scene.

        Returns:
            transformation_matrix (`np.ndarray`):
                The transformation matrix of the reward function in the scene.
        """
        if self._transformation_matrix is None:
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
        return self._transformation_matrix

    # setters for position/rotation/scale

    @position.setter
    def position(self, value: Optional[Union[float, List[float], property, Tuple, np.ndarray]] = None):
        """
        Set the position of the reward function in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The position of the reward function in the scene.
        """
        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [0.0, 0.0, 0.0]
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) != 3:
                raise ValueError("position should be of size 3 (X, Y, Z)")
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
                value = [float(v) for v in value]
            else:
                raise TypeError("Position must be a list of 3 numbers")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_position = np.array(value)
        if not np.array_equal(self._position, new_position):
            self._position = new_position
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

            self._post_asset_modification()

    @rotation.setter
    def rotation(self, value: Optional[Union[float, List[float], property, Tuple, np.ndarray]] = None):
        """
        Set the rotation of the reward function in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The rotation of the reward function in the scene.
        """
        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [0.0, 0.0, 0.0, 1.0]
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
                value = rotation_from_euler_degrees(*value)
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 4:
                value = [float(v) for v in value]
            else:
                raise ValueError("Rotation should be of size 3 (Euler angles) or 4 (Quaternions")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_rotation = np.array(value) / np.linalg.norm(value)
        if not np.array_equal(self._rotation, new_rotation):
            self._rotation = new_rotation
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

            self._post_asset_modification()

    @scaling.setter
    def scaling(self, value: Optional[Union[float, List[float], property, Tuple, np.ndarray]] = None):
        """
        Set the scaling of the reward function in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The scaling of the reward function in the scene.
        """
        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [1.0, 1.0, 1.0]
            elif isinstance(value, (int, float)):
                value = [value, value, value]
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
                value = [float(v) for v in value]
            elif not isinstance(value, np.ndarray):
                raise TypeError("Scale must be a float or a list of 3 numbers")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_scaling = np.array(value)
        if not np.array_equal(self._scaling, new_scaling):
            self._scaling = new_scaling
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

            self._post_asset_modification()

    @transformation_matrix.setter
    def transformation_matrix(self, value: Optional[Union[float, List[float], property, Tuple, np.ndarray]] = None):
        """
        Set the transformation matrix of the reward function in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The transformation matrix of the reward function in the scene.
        """
        # Default to setting up from TRS if None
        if (value is None or isinstance(value, property)) and (
            self._position is not None and self._rotation is not None and self._scaling is not None
        ):
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
            return

        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            elif not isinstance(value, (list, tuple, np.ndarray)):
                raise TypeError("Transformation matrix must be a list of 4 lists of 4 numbers")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_transformation_matrix = np.array(value)
        if not np.array_equal(self._transformation_matrix, new_transformation_matrix):
            self._transformation_matrix = new_transformation_matrix

            translation, rotation, scale = get_trs_from_transform_matrix(self._transformation_matrix)
            self._position = translation
            self._rotation = rotation
            self._scaling = scale

            self._post_asset_modification()
