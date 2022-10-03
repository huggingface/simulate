from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel


@dataclass_json
@dataclass
class TextureInfo(BaseModel):
    """
    Reference to a texture.

    Properties:
    index (integer) The index of the texture. (Required)
    texCoord (integer) The set index of texture's TEXCOORD attribute used for texture coordinate mapping. (Optional,
        default: 0)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    index: Optional[int] = None
    texCoord: Optional[int] = None
