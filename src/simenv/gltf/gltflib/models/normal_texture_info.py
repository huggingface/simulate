from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .texture_info import TextureInfo


@dataclass_json
@dataclass
class NormalTextureInfo(TextureInfo):
    """
    Material Normal Texture Info

    Properties:
    index (integer) The index of the texture. (Required)
    texCoord (integer) The set index of texture's TEXCOORD attribute used for texture coordinate mapping. (Optional,
        default: 0)
    scale (number) The scalar multiplier applied to each normal vector of the normal texture. (Optional, default: 1)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    scale: Optional[float] = None
