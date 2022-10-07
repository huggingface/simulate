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
