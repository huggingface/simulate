import itertools
from cmath import inf
from dataclasses import dataclass
from typing import Any, List, Optional, Union

import numpy as np
from dataclasses_json import dataclass_json


try:
    from gym import spaces
except ImportError:
    pass


ALLOWED_STATE_SENSOR_PROPERTIES = {
    "position": 3,
    "position.x": 1,
    "position.y": 1,
    "position.z": 1,
    "rotation": 3,
    "rotation.x": 1,
    "rotation.y": 1,
    "rotation.z": 1,
    "distance": 1,
}


def get_state_sensor_n_properties(sensor):
    n_features = 0
    for property in sensor.properties:
        n_features += ALLOWED_STATE_SENSOR_PROPERTIES[property]

    return n_features


@dataclass_json
@dataclass
class CameraSensor:
    """A Camera sensor (just a pointer to a Camera object)

    Attributes:
        camera: Reference (or string name) of a Camera asset in the scene
    """

    camera: Any


@dataclass_json
@dataclass
class StateSensor:
    """A State sensor: pointer to two assets whose positions/rotations are used to compute an observation

    Attributes:
        target_entity: Reference (or string name) of the target Asset in the scene
        reference_entity: Reference (or string name) of the reference Asset in the scene
            If no reference is provided we use the world as a reference
        type: How should we compute the observation, selected in the list of:
            - "position": the position of the target asset
            - "rotation": the rotation of the target asset
            - "distance": the distance to the target asset (default)
    """

    target_entity: Any
    reference_entity: Optional[Any] = None
    properties: Optional[List[str]] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = ["distance"]
        elif any(properties_ not in ALLOWED_STATE_SENSOR_PROPERTIES for properties_ in self.properties):
            raise ValueError(
                f"The properties {self.properties} is not a valid StateSensor properties"
                f"\nAllowed properties are: {ALLOWED_STATE_SENSOR_PROPERTIES}"
            )


@dataclass_json
@dataclass
class RaycastSensor:
    """A Raycast sensor: cast a ray to get an observation"""

    n_rays: int = 1
    axis: Optional[List[float]] = None

    def __post_init__(self):
        raise NotImplementedError


def map_sensors_to_spaces(sensor: Union[CameraSensor, StateSensor, RaycastSensor]) -> spaces.Space:
    if isinstance(sensor, CameraSensor):
        return spaces.Box(low=0, high=255, shape=[3, sensor.camera.height, sensor.camera.width], dtype=np.uint8)
    elif isinstance(sensor, StateSensor):
        return spaces.Box(low=-inf, high=inf, shape=[get_state_sensor_n_properties(sensor)], dtype=np.float32)
    raise NotImplementedError(
        f"This sensor ({type(sensor)})is not yet implemented " f"as an RlAgent type of observation."
    )
