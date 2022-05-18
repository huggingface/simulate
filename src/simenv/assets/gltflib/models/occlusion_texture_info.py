from dataclasses import dataclass
from typing import Optional

from dataclasses_json import dataclass_json

from .texture_info import TextureInfo


@dataclass_json
@dataclass
class OcclusionTextureInfo(TextureInfo):
    """
    Material Occlusion Texture Info

    Properties:
    index (integer) The index of the texture. (Required)
    texCoord (integer) The set index of texture's TEXCOORD attribute used for texture coordinate mapping. (Optional,
        default: 0)
    strength (number) A scalar multiplier controlling the amount of occlusion applied. (Optional, default: 1)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    strength: Optional[float] = None
