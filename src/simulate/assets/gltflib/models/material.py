# Copyright 2022 The HuggingFace Authors.
# Copyright (c) 2019 Sergey Krilov
# Copyright (c) 2018 Luke Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Lint as: python3
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .named_base_model import NamedBaseModel
from .normal_texture_info import NormalTextureInfo
from .occlusion_texture_info import OcclusionTextureInfo
from .pbr_metallic_roughness import PBRMetallicRoughness
from .texture_info import TextureInfo


@dataclass_json
@dataclass
class Material(NamedBaseModel):
    """
    The material appearance of a primitive.

    Properties:
    name (string) The user-defined name of this object. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)
    pbrMetallicRoughness (object) A set of parameter values that are used to define the metallic-roughness material
        model from Physically-Based Rendering (PBR) methodology. When not specified, all the default values of
        pbrMetallicRoughness apply. (Optional)
    normalTexture (object) The normal map texture. (Optional)
    occlusionTexture (object) The occlusion map texture. (Optional)
    emissiveTexture (object) The emissive map texture. (Optional)
    emissiveFactor (number[3]) The emissive color of the material. (Optional, default: [0,0,0])
    alphaMode (string) The alpha rendering mode of the material. (Optional, default: "OPAQUE")
    alphaCutoff (number) The alpha cutoff value of the material. (Optional, default: 0.5)
    doubleSided (boolean) Specifies whether the material is double-sided. (Optional, default: false)
    """

    pbrMetallicRoughness: Optional[PBRMetallicRoughness] = None
    normalTexture: Optional[NormalTextureInfo] = None
    occlusionTexture: Optional[OcclusionTextureInfo] = None
    emissiveTexture: Optional[TextureInfo] = None
    emissiveFactor: Optional[List[float]] = None
    alphaMode: Optional[str] = None
    alphaCutoff: Optional[float] = None
    doubleSided: Optional[bool] = None
