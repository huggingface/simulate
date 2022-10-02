from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Skin(NamedBaseModel):
    """
    Joints and matrices defining a skin.

    Properties:
    inverseBindMatrices (integer): The index of the accessor containing the floating-point 4x4 inverse-bind matrices.
        The default is that each matrix is a 4x4 identity matrix, which implies that inverse-bind matrices were
        pre-applied. (Optional)
    skeleton (integer): The index of the node used as a skeleton root. (Optional)
    joints (integer [1-*]): Indices of skeleton nodes, used as joints in this skin. (Required)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    inverseBindMatrices: Optional[int] = None
    skeleton: Optional[int] = None
    joints: Optional[List[int]] = None
