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
""" Sensors for the RL Agent."""
import itertools
from cmath import inf
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, List, Optional, Tuple, Union

import numpy as np
from dataclasses_json import dataclass_json

from ..utils import logging
from .asset import Asset, get_transform_from_trs, get_trs_from_transform_matrix, rotation_from_euler_degrees
from .gltf_extension import GltfExtensionMixin


logger = logging.get_logger(__name__)

try:
    from gym import spaces
except ImportError:
    # Our implementation of gym space classes if gym is not installed
    logger.warning(
        "The gym library is not installed, falling back our implementation of gym.spaces. "
        "To remove this message pip install simulate[rl]"
    )
    from . import spaces


ALLOWED_STATE_SENSOR_PROPERTIES = {
    "position": 3,
    "position.x": 1,
    "position.y": 1,
    "position.z": 1,
    "velocity": 3,
    "velocity.x": 1,
    "velocity.y": 1,
    "velocity.z": 1,
    "rotation": 3,
    "rotation.x": 1,
    "rotation.y": 1,
    "rotation.z": 1,
    "angular_velocity": 3,
    "angular_velocity.x": 1,
    "angular_velocity.y": 1,
    "angular_velocity.z": 1,
    "distance": 1,
}


def get_state_sensor_n_properties(sensor: Union["StateSensor", "RaycastSensor"]) -> int:
    """
    Get the number of properties of a state sensor.

    Args:
        sensor (`StateSensor` or `RaycastSensor`):
            The sensor to get the number of properties from.

    Returns:
        n_features (`int`):
            The number of properties of the sensor.
    """
    n_features = 0
    for sensor_property in sensor.properties:
        n_features += ALLOWED_STATE_SENSOR_PROPERTIES[sensor_property]

    return n_features


@dataclass
class StateSensor(Asset, GltfExtensionMixin, gltf_extension_name="HF_state_sensors", object_type="node"):
    """
    A State sensor: pointer to two assets whose positions/rotations are used to compute an observation

    Args:
        target_entity (`Asset` or `str`, *optional*, defaults to `None`):
            Reference or name of the target Asset in the scene.
        reference_entity (`Asset` or `str`, *optional*, defaults to `None`):
            Reference or name of the reference Asset in the scene.
            If no reference is provided we use the world as a reference.
        properties (`str` or `List[str]`, *optional*, defaults to `["distance"]`):
            List of properties to extract from the sensor. Allowed properties are:
            [
                "position", "position.x", "position.y", "position.z",
                "velocity", "velocity.x", "velocity.y", "velocity.z",
                "rotation", "rotation.x", "rotation.y", "rotation.z",
                "angular_velocity", "angular_velocity.x", "angular_velocity.y", "angular_velocity.z",
                "distance"
            ]
        sensor_tag (`str`, *optional*, defaults to `"StateSensor"`):
            Type of sensor. Allowed values are: "position", "velocity", "rotation", "angular_velocity", "distance".

        name (`str`, *optional*, defaults to `None`):
            Name of the sensor.
        position (`List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the sensor in the scene.
        rotation (`List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Rotation of the sensor in the scene.
        scaling (`List[float]`, *optional*, defaults to `[1, 1, 1]`):
            Scaling of the sensor in the scene.
        transformation_matrix (`List[float]`, *optional*, defaults to `None`):
            Transformation matrix of the sensor in the scene.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the sensor in the scene.
        children (`List[Asset]`, *optional*, defaults to `None`):
            Children of the sensor in the scene.
        created_from_file (`str`, *optional*, defaults to `None`):
            The path to the file from which the sensor was created.
    """

    target_entity: Optional[Any] = None
    reference_entity: Optional[Any] = None
    properties: Optional[Union[str, List[str]]] = None
    sensor_tag: str = "StateSensor"

    name: InitVar[Optional[str]] = None
    position: InitVar[Optional[List[float]]] = None
    rotation: InitVar[Optional[List[float]]] = None
    scaling: InitVar[Optional[Union[float, List[float]]]] = None
    transformation_matrix: InitVar[Optional[List[float]]] = None
    parent: InitVar[Optional["Asset"]] = None
    children: InitVar[Optional[List["Asset"]]] = None
    created_from_file: InitVar[Optional[str]] = None

    __NEW_ID: ClassVar[Any] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __post_init__(
        self, name, position, rotation, scaling, transformation_matrix, parent, children, created_from_file
    ):
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

        if self.properties is None:
            self.properties = ["distance"]
        if not isinstance(self.properties, (list, tuple)):
            self.properties = [self.properties]
        elif any(properties_ not in ALLOWED_STATE_SENSOR_PROPERTIES for properties_ in self.properties):
            raise ValueError(
                f"The properties {self.properties} is not a valid StateSensor properties"
                f"\nAllowed properties are: {ALLOWED_STATE_SENSOR_PROPERTIES}"
            )

    @property
    def observation_space(self) -> spaces.Box:
        """
        Get the observation space of the sensor.

        Returns:
            observation_space (`gym.spaces.Box`):
                The observation space of the sensor.
        """
        return spaces.Box(low=-inf, high=inf, shape=[get_state_sensor_n_properties(self)], dtype=np.float32)

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
        Get the position of the sensor in the scene.

        Returns:
            position (`List[float]` or `np.ndarray`):
                The position of the sensor in the scene.
        """
        return self._position

    @property
    def rotation(self) -> Union[List[float], np.ndarray]:
        """
        Get the rotation of the sensor in the scene.

        Returns:
            rotation (`List[float]` or `np.ndarray`):
                The rotation of the sensor in the scene.
        """
        return self._rotation

    @property
    def scaling(self) -> Union[List[float], np.ndarray]:
        """
        Get the scaling of the sensor in the scene.

        Returns:
            scaling (`List[float]` or `np.ndarray`):
                The scaling of the sensor in the scene.
        """
        return self._scaling

    @property
    def transformation_matrix(self) -> Union[List[float], np.ndarray]:
        """
        Get the transformation matrix of the sensor in the scene.

        Returns:
            transformation_matrix (`List[float]` or `np.ndarray`):
                The transformation matrix of the sensor in the scene.
        """
        if self._transformation_matrix is None:
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
        return self._transformation_matrix

    # setters for position/rotation/scale

    @position.setter
    def position(self, value: Optional[Union[float, List[float], property, Tuple, np.ndarray]] = None):
        """
        Set the position of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The position of the sensor in the scene.
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
        Set the rotation of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The rotation of the sensor in the scene.
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
        Set the scaling of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The scaling of the sensor in the scene.
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
        Set the transformation matrix of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The transformation matrix of the sensor in the scene.
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


@dataclass_json
@dataclass
class RaycastSensor(Asset, GltfExtensionMixin, gltf_extension_name="HF_raycast_sensors", object_type="node"):
    """
    A Raycast sensor: cast a ray to get an observation.

    Args:
        n_horizontal_rays (`int`, *optional*, defaults to `1`):
            The number of horizontal rays to cast.
        n_vertical_rays (`int`, *optional*, defaults to `1`):
            The number of vertical rays to cast.
        horizontal_fov (`float`, *optional*, defaults to `0.0`):
            The horizontal field of view of the sensor.
        vertical_fov (`float`, *optional*, defaults to `0.0`):
            The vertical field of view of the sensor.
        ray_length (`float`, *optional*, defaults to `100.0`):
            The length of the ray to cast.
        sensor_tag (`str`, *optional*, defaults to `"RaycastSensor"`):
            The tag of the sensor.

        name (`str`, *optional*, defaults to `None`):
            The name of the sensor.
        position (`List[float]`, *optional*, defaults to `None`):
            The position of the sensor in the scene.
        rotation (`List[float]`, *optional*, defaults to `None`):
            The rotation of the sensor in the scene.
        scaling (`List[float]`, *optional*, defaults to `None`):
            The scaling of the sensor in the scene.
        transformation_matrix (`List[float]`, *optional*, defaults to `None`):
            The transformation matrix of the sensor in the scene.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the sensor.
        children (`List[Asset]`, *optional*, defaults to `None`):
            The children of the sensor.
        created_from_file (`str`, *optional*, defaults to `None`):
            The path to the file from which the sensor was created.
    """

    n_horizontal_rays: int = 1
    n_vertical_rays: int = 1
    horizontal_fov: float = 0.0
    vertical_fov: float = 0.0
    ray_length: float = 100.0
    sensor_tag: str = "RaycastSensor"

    name: InitVar[Optional[str]] = None
    position: InitVar[Optional[List[float]]] = None
    rotation: InitVar[Optional[List[float]]] = None
    scaling: InitVar[Optional[Union[float, List[float]]]] = None
    transformation_matrix: InitVar[Optional[List[float]]] = None
    parent: InitVar[Optional["Asset"]] = None
    children: InitVar[Optional[List["Asset"]]] = None
    created_from_file: InitVar[Optional[str]] = None

    __NEW_ID: ClassVar[Any] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __post_init__(
        self, name, position, rotation, scaling, transformation_matrix, parent, children, created_from_file
    ):
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

    @property
    def observation_space(self) -> spaces.Box:
        """
        Get the observation space of the sensor.

        Returns:
            observation_space (`gym.spaces.Box`):
                The observation space of the sensor.
        """
        return spaces.Box(low=-inf, high=inf, shape=[self.n_horizontal_rays * self.n_vertical_rays], dtype=np.float32)

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
        Get the position of the sensor in the scene.

        Returns:
            position (`List[float]` or `np.ndarray`):
                The position of the sensor in the scene.
        """
        return self._position

    @property
    def rotation(self) -> Union[List[float], np.ndarray]:
        """
        Get the rotation of the sensor in the scene.

        Returns:
            rotation (`List[float]` or `np.ndarray`):
                The rotation of the sensor in the scene.
        """
        return self._rotation

    @property
    def scaling(self) -> Union[List[float], np.ndarray]:
        """
        Get the scaling of the sensor in the scene.

        Returns:
            scaling (`List[float]` or `np.ndarray`):
                The scaling of the sensor in the scene.
        """
        return self._scaling

    @property
    def transformation_matrix(self) -> Union[List[float], np.ndarray]:
        """
        Get the transformation matrix of the sensor in the scene.

        Returns:
            transformation_matrix (`List[float]` or `np.ndarray`):
                The transformation matrix of the sensor in the scene.
        """
        if self._transformation_matrix is None:
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
        return self._transformation_matrix

    # setters for position/rotation/scale

    @position.setter
    def position(self, value: Optional[Union[float, List[float], property, Tuple, np.ndarray]] = None):
        """
        Set the position of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The position of the sensor in the scene.
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
        Set the rotation of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The rotation of the sensor in the scene.
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
        Set the scaling of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The scaling of the sensor in the scene.
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
        Set the transformation matrix of the sensor in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The transformation matrix of the sensor in the scene.
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
