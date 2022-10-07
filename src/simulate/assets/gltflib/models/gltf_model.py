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
import json
from dataclasses import asdict, dataclass
from typing import Any, List, Optional

from dataclasses_json import DataClassJsonMixin

from ..utils import replace_unique_id_and_remove_none
from .accessor import Accessor
from .animation import Animation
from .asset import Asset
from .base_model import BaseModel
from .buffer import Buffer
from .buffer_view import BufferView
from .camera import Camera
from .image import Image
from .material import Material
from .mesh import Mesh
from .node import Node
from .sampler import Sampler
from .scene import Scene
from .skin import Skin
from .texture import Texture


@dataclass
class GLTFModel(DataClassJsonMixin, BaseModel):
    accessors: Optional[List[Accessor]] = None
    animations: Optional[List[Animation]] = None
    asset: Optional[Asset] = None
    buffers: Optional[List[Buffer]] = None
    bufferViews: Optional[List[BufferView]] = None
    cameras: Optional[List[Camera]] = None
    images: Optional[List[Image]] = None
    materials: Optional[List[Material]] = None
    meshes: Optional[List[Mesh]] = None
    nodes: Optional[List[Node]] = None
    samplers: Optional[List[Sampler]] = None
    scene: Optional[int] = None
    scenes: Optional[List[Scene]] = None
    skins: Optional[List[Skin]] = None
    textures: Optional[List[Texture]] = None
    extensionsRequired: Optional[List[str]] = None
    extensionsUsed: Optional[List[str]] = None

    def to_json(self, **kwargs: Any) -> str:
        data = replace_unique_id_and_remove_none(asdict(self))
        return json.dumps(data, **kwargs)
