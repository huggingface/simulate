# Copyright 2022 The HuggingFace Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
""" A simenv Material."""
from dataclasses import dataclass
from typing import List, Optional

from pyvista import Texture


# TODO thom this is a very basic PBR Metrial class, mostly here to be able to load a gltf
# To be revamped and improved later


@dataclass
class PBRMetallicRoughness:
    """
    A set of parameter values that are used to define the metallic-roughness material model from Physically-Based
    Rendering (PBR) methodology.

    Properties:
    """


@dataclass
class Material:
    """
    The material appearance of a primitive.

    Properties:
    name (string) The user-defined name of this object. (Optional)

    [pbrMetallicRoughness properties]: A set of parameter values that are used to define the metallic-roughness material
        model from Physically-Based Rendering (PBR) methodology. When not specified, all the default values of
        pbrMetallicRoughness apply. (Optional)
    baseColorFactor (number[4]) The material's base color factor. (Optional, default: [1,1,1,1])
    baseColorTexture (object) The base color texture. (Optional)
    metallicFactor (number) The metalness of the material. (Optional, default: 1)
    roughnessFactor (number) The roughness of the material. (Optional, default: 1)
    metallicRoughnessTexture (object) The metallic-roughness texture. (Optional)
    extensions (object) Dictionary object with extension-specific objects. (Optional)
    extras (any) Application-specific data. (Optional)

    normalTexture (object) The normal map texture. (Optional)
    occlusionTexture (object) The occlusion map texture. (Optional)
    emissiveTexture (object) The emissive map texture. (Optional)
    emissiveFactor (number[3]) The emissive color of the material. (Optional, default: [0,0,0])
    alphaMode (string) The alpha rendering mode of the material. (Optional, default: "OPAQUE")
    alphaCutoff (number) The alpha cutoff value of the material. (Optional, default: 0.5)
    doubleSided (boolean) Specifies whether the material is double sided. (Optional, default: false)
    """

    name: Optional[str] = None

    baseColorFactor: Optional[List[float]] = None
    baseColorTexture: Optional[Texture] = None
    metallicFactor: Optional[float] = None
    roughnessFactor: Optional[float] = None
    metallicRoughnessTexture: Optional[Texture] = None

    normalTexture: Optional[Texture] = None
    occlusionTexture: Optional[Texture] = None
    emissiveTexture: Optional[Texture] = None
    emissiveFactor: Optional[List[float]] = None
    alphaMode: Optional[str] = None
    alphaCutoff: Optional[float] = None
    doubleSided: Optional[bool] = None
