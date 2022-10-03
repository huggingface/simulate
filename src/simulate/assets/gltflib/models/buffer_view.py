from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class BufferView(NamedBaseModel):
    """
    A view into a buffer generally representing a subset of the buffer.

    Properties:
    buffer (integer): The index of the buffer. (Required)
    byteOffset (integer): The offset into the buffer in bytes. (Optional, default: 0)
    byteLength (integer): The length of the bufferView in bytes. (Required)
    byteStride (integer): The stride, in bytes. (Optional)
    target (integer): The target that the GPU buffer should be bound to. (Optional)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    buffer: Optional[int] = None
    byteOffset: Optional[int] = None
    byteLength: Optional[int] = None
    byteStride: Optional[int] = None
    target: Optional[int] = None
