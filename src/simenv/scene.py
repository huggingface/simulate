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

from anytree import RenderTree
from gltflib import GLTF

from .assets import Asset, World3D
from .renderer.unity import Unity


class Scene:
    def __init__(self, renderer: Optional[str] = None, dimensionality=3, start_frame=0, end_frame=500, frame_rate=24, assets=None):

        self.renderer = None
        if renderer == "Unity":
            self.renderer = Unity(self, start_frame=start_frame, end_frame=end_frame, frame_rate=frame_rate)
        elif renderer == "Blender":
            raise NotImplementedError()
        elif renderer is None:
            pass
        else:
            raise ValueError("renderer should be selected ()")

        self.dimensionality = dimensionality
        self.root = World3D("Scene")
        self.assets = set([self.root])

        if assets is not None:
            self.add(assets)

    @classmethod
    def load_from_file(cls, file_path):
        scene = cls()
        return scene

    def add(self, assets: Union[Asset, Sequence[Asset]], exists_not_ok=False):
        """ Add an Asset or a list of Assets to the Scene together with all its descendants.
        If the parent of the Asset is not set (None), the Asset will be set to be a child of the Scene root node
        """
        if isinstance(assets, Asset):
            assets = [assets]
        
        for asset in assets:
            if asset.parent is None:
                asset.parent = self.root
            elif asset.parent not in self.assets:
                raise ValueError("The parent of the asset to add must be either None or an asset in the Scene")

            if exists_not_ok and asset in self.assets:
                raise ValueError("Asset is already in the Scene and exists_not_ok is True")

            self.assets.add(asset)
            for child in asset.descendants:
                # Add all the descendants
                self.assets.add(child)

    def remove(self, assets: Union[Asset, Sequence[Asset]], not_exist_ok=False):
        """ Remove an Asset or a list of Assets to the Scene together with all its descendants."""
        if isinstance(assets, Asset):
            assets = [assets]
        
        for asset in assets:
            if not not_exist_ok and asset not in self.assets:
                raise ValueError("Asset is not in the scene")

            asset.parent = None
            self.assets.discard(asset)
            for child in asset.descendants:
                # Remove all the descendants
                self.assets.discard(child)

    def __iadd__(self, asset: Asset):
        self.add(asset)
        return self

    def __isub__(self, asset: Asset):
        self.remove(asset)
        return self

    def __repr__(self):
        return RenderTree(self.root).by_attr(lambda n: str(n))
