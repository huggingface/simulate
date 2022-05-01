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
""" A simenv Scene - Host a level or Scene."""
from typing import Optional, Sequence, Union
from dataclasses import make_dataclass, fields

from .assets.anytree import RenderTree

from .assets import Asset, World3D, NodeMixin
from .gltf_export import export_assets_to_gltf
from .gltf_import import load_gltf_in_assets
from .renderer.unity import Unity


class UnsetRendererError(Exception):
    pass


class Scene(NodeMixin):
    def __init__(
        self,
        engine: Optional[str] = None,
        dimensionality=3,
        start_frame=0,
        end_frame=500,
        frame_rate=24,
        assets=None,
    ):

        self.engine = None
        if engine == "Unity":
            self.engine = Unity(self, start_frame=start_frame, end_frame=end_frame, frame_rate=frame_rate)
        elif engine == "Blender":
            raise NotImplementedError()
        elif engine is None:
            pass
        else:
            raise ValueError("engine should be selected ()")

        self.dimensionality = dimensionality

    @classmethod
    def from_gltf(cls, file_path, **kwargs):
        assets = load_gltf_in_assets(file_path)
        return cls(assets=assets, **kwargs)

    def render(self):
        gltf_file_path = export_assets_to_gltf(self.assets)
        if self.engine is not None:
            self.engine.send_gltf(gltf_file_path)
        else:
            raise UnsetRendererError()

    def __repr__(self):
        return f"Scene(dimensionality={self.dimensionality}, engine='{self.engine}')\n{RenderTree(self).print_tree()}"
