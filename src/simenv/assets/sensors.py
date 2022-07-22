from typing import Optional
from simenv.assets.asset import Asset
from .camera import Camera

import itertools
import numpy as np
try:
    from gym import spaces
except ImportError:
    pass


def map_sensors_to_spaces(asset: Asset):
    if isinstance(asset, CameraSensor):
        return spaces.Box(low=0, high=255, shape=[3, asset.height, asset.width], dtype=np.uint8)
    raise NotImplementedError(
        f"This Asset ({type(Asset)})is not yet implemented " f"as an RlAgent type of observation."
    )

class Sensor():
    @property
    def sensor_name(self):
        return type(self).__name__

class CameraSensor(Camera, Sensor):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    def __init__(self, **kwargs):
        Camera.__init__(self, **kwargs)


class StateSensor(Asset, Sensor):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming
    def __init__(self, entity: Optional[Asset]=None, property: Optional[str]="position", **kwargs):
        Asset.__init__(self, **kwargs)
        self.entity = entity
        self.property = property
        pass


class RaycastSensor(Asset, Sensor):
    def __init__(self, n_rays=1,  **kwargs):
        pass


