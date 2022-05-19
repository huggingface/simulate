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
from .engine import PyVistaEngine, UnityEngine
from .gltf_import import load_gltf_as_tree


class UnsetRendererError(Exception):
    pass


class SceneNotBuiltError(Exception):
    pass


class Scene(Asset):
    def __init__(self, engine: Optional[str] = None, name: Optional[str] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.engine = None
        self._built = False
        if engine == "Unity":
            self.engine = UnityEngine(self)
        elif engine == "Blender":
            raise NotImplementedError()
        elif engine == "pyvista" or engine is None:
            self.engine = PyVistaEngine(self)
        else:
            raise ValueError("engine should be selected ()")

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
            position=root.position,
            rotation=root.rotation,
            scaling=root.scaling,
            children=nodes,
            **kwargs,
        )

    def clear(self):
        """ " Remove all assets in the scene."""
        self.tree_children = []
        return self

    def _get_decendants_of_class_type(self, class_type):
        result = []
        for child in self.tree_descendants:
            if isinstance(child, class_type):
                result.append(child)

        return result

    def get_agents(self):
        # search all nodes for agents classes and then return in list
        return self._get_decendants_of_class_type(sm.RLAgent)

    def show(self):
        """Render the Scene using the engine if provided."""
        if self.engine is None:
            raise UnsetRendererError()

        self.engine.show()
        self._built = True

    def step(self, action):
        """Step the Scene using the engine if provided."""

        if not self._built: raise SceneNotBuiltError()
        if self.engine is None: raise UnsetRendererError()

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
