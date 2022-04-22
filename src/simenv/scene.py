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
from anytree import RenderTree
from typing import Optional

from .assets import World3D, Asset
from .renderer.unity import Unity


class Scene:
    def __init__(self, renderer: Optional[str]=None, dimensionality=3, start_frame=0, end_frame=500, frame_rate=24):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate

        self.renderer = None
        if renderer == "Unity":
            self.renderer = Unity(self)

        self.dimensionality = dimensionality
        self.root = World3D("Scene")
        self.assets = set([self.root])

    def add(self, asset: Asset):
        if asset in self.assets:
            raise ValueError("Asset is already in the scene")
        if asset.parent is None:
            asset.parent = self.root
        self.assets.add(asset)

    def __iadd__(self, asset: Asset):
        self.add(asset)
        return self

    def remove(self, asset: Asset, not_exist_ok=False):
        if not not_exist_ok and asset not in self.assets:
            raise ValueError("Asset is not in the scene")

        self.assets.remove(asset)
        descendants = asset.descendants
        for child in descendants:
            # Remove elements from the set
            self.assets.discard(child)

    def __repr__(self):
        return RenderTree(self.root).by_attr(lambda n: f"{n.name} ({ n.__class__.__name__})")
