from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel
from .orthographic_camera_info import OrthographicCameraInfo
from .perspective_camera_info import PerspectiveCameraInfo


@dataclass_json
@dataclass
class Camera(NamedBaseModel):
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
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    orthographic: Optional[OrthographicCameraInfo] = None
    perspective: Optional[PerspectiveCameraInfo] = None
    type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
