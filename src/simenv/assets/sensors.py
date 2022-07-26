import itertools
from cmath import inf
from typing import List, Optional

import numpy as np

from simenv.assets.asset import Asset

from .camera import Camera


try:
    from gym import spaces
except ImportError:
    pass


def map_sensors_to_spaces(sensor: "Sensor"):
    if isinstance(sensor, CameraSensor):
        return spaces.Box(low=0, high=255, shape=[3, sensor.height, sensor.width], dtype=np.uint8)
    elif isinstance(sensor, StateSensor):
        return spaces.Box(low=-inf, high=inf, shape=[get_state_sensor_n_properties(sensor)], dtype=np.float32)
    raise NotImplementedError(
        f"This Asset ({type(Asset)})is not yet implemented " f"as an RlAgent type of observation."
    )


def get_state_sensor_n_properties(sensor):
    VALID_PROPERTIES = {
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

    n_features = 0
    for property in sensor.properties:
        if property not in VALID_PROPERTIES.keys():
            print(f"The property {property} is not a valid StateSensor property")
            raise KeyError

        n_features += VALID_PROPERTIES[property]

    return n_features


class Sensor:
    @property
    def sensor_name(self):
        return type(self).__name__


class CameraSensor(Camera, Sensor):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(self, **kwargs):
        Camera.__init__(self, **kwargs)


class StateSensor(Asset, Sensor):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        reference_entity: Optional[Asset] = None,
        target_entity: Optional[Asset] = None,
        properties: Optional[List[str]] = ["position"],
        **kwargs,
    ):
        Asset.__init__(self, **kwargs)
        self.reference_entity = reference_entity
        self.target_entity = target_entity
        self.properties = properties  # e.g. [position, rotatation, position.x, distance]


class RaycastSensor(Asset, Sensor):
    def __init__(self, n_rays=1, **kwargs):
        raise NotImplementedError
