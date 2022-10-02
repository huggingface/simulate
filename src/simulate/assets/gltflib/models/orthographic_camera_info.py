from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class OrthographicCameraInfo(BaseModel):
    """
    An orthographic camera containing properties to create an orthographic projection matrix.

    Properties:
    xmag (number) The floating-point horizontal magnification of the view. (Required)
    ymag (number) The floating-point vertical magnification of the view. (Required)
    zfar (number) The floating-point distance to the far clipping plane. zfar must be greater than znear. (Required)
    znear (number) The floating-point distance to the near clipping plane. (Required)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    xmag: Optional[float] = None
    ymag: Optional[float] = None
    zfar: Optional[float] = None
    znear: Optional[float] = None
