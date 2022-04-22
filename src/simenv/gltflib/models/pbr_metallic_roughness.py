from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .base_model import BaseModel
from .texture_info import TextureInfo


@dataclass_json
@dataclass
class PBRMetallicRoughness(BaseModel):
    """
    A set of parameter values that are used to define the metallic-roughness material model from Physically-Based
    Rendering (PBR) methodology.

    Properties:
    baseColorFactor (number[4]) The material's base color factor. (Optional, default: [1,1,1,1])
    baseColorTexture (object) The base color texture. (Optional)
    metallicFactor (number) The metalness of the material. (Optional, default: 1)
    roughnessFactor (number) The roughness of the material. (Optional, default: 1)
    metallicRoughnessTexture (object) The metallic-roughness texture. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    """

    baseColorFactor: Optional[List[float]] = None
    baseColorTexture: Optional[TextureInfo] = None
    metallicFactor: Optional[float] = None
    roughnessFactor: Optional[float] = None
    metallicRoughnessTexture: Optional[TextureInfo] = None
