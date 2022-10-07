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
""" A generic engine."""

import typing


if typing.TYPE_CHECKING:
    from ..assets.asset import Asset
    from ..scene import Scene


class Engine:
    """
    Generic Engine class from which to inherit to implement integrations for any engine.

    Args:
        scene (`Scene`):
            The scene to simulate.
        auto_update (`bool`, *optional*, defaults to `True`):
            Whether to automatically update the scene when an asset is updated.
    """

    def __init__(self, scene: "Scene", auto_update: bool = True):
        self._scene = scene
        self.auto_update = auto_update

    def update_asset(self, asset_node: "Asset"):
        """Add an asset or update its location and all its children in the scene."""
        pass

    def remove_asset(self, asset_node: "Asset"):
        """Remove an asset and all its children in the scene."""
        pass

    def regenerate_scene(self):
        """Recreate all the assets in the scene (recreate the scene)."""
        pass

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __exit__(self):
        self.close()

    def close(self):
        """Close the engine."""
        pass
