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
from typing import Optional

import simenv as sm

from .assets import Asset
from .assets.anytree import RenderTree
from .gltf_export import tree_as_glb_bytes
from .gltf_import import load_gltf_as_tree
from .renderer.unity import Unity


class UnsetRendererError(Exception):
    pass


class SceneNotBuiltError(Exception):
    pass


class Scene(Asset):
    def __init__(
        self,
        engine: Optional[str] = None,
        start_frame=0,
        end_frame=500,
        frame_rate=24,
        children=None,
        name=None,
        translation=None,
        rotation=None,
        scale=None,
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

        self._built = False
        super().__init__(name=name, translation=translation, rotation=rotation, scale=scale, children=children)

    @classmethod
    def from_gltf(cls, file_path, **kwargs):
        """Load a Scene from a GLTF file."""
        nodes = load_gltf_as_tree(file_path)
        if len(nodes) == 1:
            root = nodes[0]  # If we have a single root node in the GLTF, we use it for our scene
            nodes = root.tree_children
        else:
            root = Asset(name="Scene")  # Otherwise we build a main root node
        return cls(
            name=root.name,
            translation=root.translation,
            rotation=root.rotation,
            scale=root.scale,
            children=nodes,
            **kwargs,
        )

    def _get_decendants_of_class_type(self, class_type):
        result = []
        for child in self.tree_descendants:
            if isinstance(child, class_type):
                result.append(child)

        return result

    def get_agents(self):
        # search all nodes for agents classes and then return in list
        return self._get_decendants_of_class_type(sm.RL_Agent)

    def build(self):
        """Render the Scene using the engine if provided."""
        if self.engine is None:
            raise UnsetRendererError()

        self.engine.send_gltf(tree_as_glb_bytes(self))
        self._built = True

    def step(self, action):
        """Step the Scene using the engine if provided."""

        if not self._built: raise SceneNotBuiltError()
        if self.engine is None:raise UnsetRendererError()

        return self.engine.step(action)

    def get_observation(self):
        """Step the Scene using the engine if provided."""
        if not self._built: raise SceneNotBuiltError()
        if self.engine is None: raise UnsetRendererError()

        return self.engine.get_observation()

    def __repr__(self):
        return f"Scene(dimensionality={self.dimensionality}, engine='{self.engine}')\n{RenderTree(self).print_tree()}"

    def close(self):
        self.engine.close()
