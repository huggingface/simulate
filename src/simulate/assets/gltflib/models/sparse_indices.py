from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class SparseIndices(BaseModel):
    """
    Indices of those attributes that deviate from their initialization value.

    Properties:
    bufferView (integer) The index of the bufferView with sparse indices. Referenced bufferView can't have ARRAY_BUFFER
        or ELEMENT_ARRAY_BUFFER target. (Required)
    byteOffset (integer) The offset relative to the start of the bufferView in bytes. Must be aligned. (Optional)
    componentType (integer) The indices data type. (Required)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    bufferView: Optional[int] = None
    byteOffset: Optional[int] = None
    componentType: Optional[int] = None
