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

from .assets import Asset, World3D
from .gltf_export import export_assets_to_gltf
from .gltf_import import load_gltf_in_assets
from .renderer.unity import Unity


class UnsetRendererError(Exception):
    pass


class Scene:
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

        self.assets = None
        self._assets = set()

        if assets is not None:
            if isinstance(assets, Asset):
                self.assets = assets
                self.add(assets)
            elif isinstance(assets, list) and len(assets) and isinstance(assets[0], Asset):
                self.assets = assets[0]
                self.add(assets)
            else:
                raise ValueError("Provided assets should be an Asset or a list of Assets")
        else:
            self.assets = World3D("Scene")
            self._assets = set([self.assets])

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

    def add(self, assets: Union[Asset, Sequence[Asset]], exists_not_ok=False):
        """ Add an Asset or a list of Assets to the Scene together with all its descendants.
            If the parent of the Asset is not set (None), the Asset will be set to be a child of the Scene root node
        """
        if isinstance(assets, Asset):
            assets = [assets]

        for asset in assets:
            if asset.parent is None:
                asset.parent = self.assets if asset != self.assets else None
            elif asset.parent not in self._assets:
                raise ValueError("The parent of the asset to add must be either None or an asset in the Scene")

            if exists_not_ok and asset in self._assets:
                raise ValueError("Asset is already in the Scene and exists_not_ok is True")

            self._assets.add(asset)
            for child in asset.descendants:
                # Add all the descendants
                self._assets.add(child)

    def remove(self, assets: Union[Asset, Sequence[Asset]], not_exist_ok=False):
        """Remove an Asset or a list of Assets to the Scene together with all its descendants."""
        if isinstance(assets, Asset):
            assets = [assets]

        for asset in assets:
            if not not_exist_ok and asset not in self._assets:
                raise ValueError("Asset is not in the scene")

            asset.parent = None
            self._assets.discard(asset)
            for child in asset.descendants:
                # Remove all the descendants
                self._assets.discard(child)

    def __iadd__(self, asset: Asset):
        self.add(asset)
        return self

    def __isub__(self, asset: Asset):
        self.remove(asset)
        return self

    def __repr__(self):
        return f"Scene(dimensionality={self.dimensionality}, engine='{self.engine}, root={self.assets}')\n{RenderTree(self.root).print_tree()}"
