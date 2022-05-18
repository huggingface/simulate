from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Attributes:
    """
    Helper type for describing the attributes of a primitive. Each property corresponds to mesh attribute semantic and
    each value is the index of the accessor containing the attribute's data.
    """

    POSITION: Optional[int] = None
    NORMAL: Optional[int] = None
    TANGENT: Optional[int] = None
    TEXCOORD_0: Optional[int] = None
    TEXCOORD_1: Optional[int] = None
    COLOR_0: Optional[int] = None
    JOINTS_0: Optional[int] = None
    WEIGHTS_0: Optional[int] = None
