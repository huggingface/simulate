from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class SparseValues(BaseModel):
    """
    Array of size accessor.sparse.count times number of components storing the displaced accessor attributes pointed by
    accessor.sparse.indices.

    Properties:
    bufferView (integer) The index of the bufferView with sparse values. Referenced bufferView can't have ARRAY_BUFFER
        or ELEMENT_ARRAY_BUFFER target. (Required)
    byteOffset (integer) The offset relative to the start of the bufferView in bytes. Must be aligned. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    bufferView: Optional[int] = None
    byteOffset: Optional[int] = None
