from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class PerspectiveCameraInfo(BaseModel):
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
    yfov: Optional[float] = None
    zfar: Optional[float] = None
    znear: Optional[float] = None
