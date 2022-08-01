from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class PerspectiveCameraInfo:
    """
    A perspective camera containing properties to create a perspective projection matrix.

    Properties:
    aspectRatio (number) The floating-point aspect ratio of the field of view. (Optional)
    yfov (number) The floating-point vertical field of view in radians.dd (Required)
    zfar (number) The floating-point distance to the far clipping plane. (Optional)
    znear (number) The floating-point distance to the near clipping plane.dd (Required)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    aspectRatio: Optional[float] = None
    yfov: float = None
    zfar: Optional[float] = None
    znear: float = None


@dataclass_json
@dataclass
class OrthographicCameraInfo:
    """
    An orthographic camera containing properties to create an orthographic projection matrix.

    Properties:
    xmag (number) The floating-point horizontal magnification of the view. (Required)
    ymag (number) The floating-point vertical magnification of the view. (Required)
    zfar (number) The floating-point distance to the far clipping plane. zfar must be greater than znear. (Required)
    znear (number) The floating-point distance to the near clipping plane. (Required)
    """

    xmag: float = None
    ymag: float = None
    zfar: float = None
    znear: float = None


@dataclass_json
@dataclass
class HFCameraSensor:
    """
    A camera's projection. A node can reference a camera to apply a transform to place the camera in the scene.

    Properties:
    orthographic (object) An orthographic camera containing properties to create an orthographic projection matrix.
        (Optional)
    perspective (object) A perspective camera containing properties to create a perspective projection matrix.
        (Optional)
    type (string) Specifies if the camera uses a perspective or orthographic projection. (Required)
    name (string) The user-defined name of this object. (Optional)
    width (int) The width of the camera render result. (Optional)
    height (int) The height of the camera render result. (Optional)s
    """

    orthographic: Optional[OrthographicCameraInfo] = None
    perspective: Optional[PerspectiveCameraInfo] = None
    type: str = None
    width: int = None
    height: int = None


@dataclass_json
@dataclass
class HFCameraSensors:
    """
    A camera sensor within a scene. This extension defines Camera Sensors.

    Properties:
    camera_sensors (list) Array of Camera Sensors
    """

    camera_sensors: Optional[List[HFCameraSensor]] = None
    camera_sensor: Optional[int] = None


@dataclass_json
@dataclass
class HFStateSensor:
    """
    A State Sensor, which measures properties such a position of an object
    """

    reference_entity_name: Optional[str] = None
    target_entity_name: Optional[str] = None
    properties: Optional[List[str]] = None


@dataclass_json
@dataclass
class HFStateSensors:
    """
    A state sensor within a scene.

    Properties:
    state_sensors (list) Array of State Sensors
    """

    state_sensors: Optional[List[HFStateSensor]] = None
    state_sensor: Optional[int] = None
