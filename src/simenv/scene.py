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

from huggingface_hub import Repository, hf_hub_download

import simenv as sm

from .assets import Asset
from .assets.anytree import RenderTree
from .engine import PyVistaEngine, UnityEngine
from .gltf_export import save_as_gltf_file
from .gltf_import import load_gltf_as_tree


class UnsetRendererError(Exception):
    pass


class SceneNotBuiltError(Exception):
    pass


class Scene(Asset):
    def __init__(
        self,
        engine: Optional[str] = None,
        name: Optional[str] = None,
        created_from_file: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.engine = None
        self._built = False
        self._created_from_file = created_from_file
        if engine == "Unity":
            self.engine = UnityEngine(self)
        elif engine == "Blender":
            raise NotImplementedError()
        elif engine == "pyvista" or engine is None:
            self.engine = PyVistaEngine(self)
        else:
            raise ValueError("engine should be selected ()")

    @classmethod
    def load_from_hub(
        cls,
        repo_id: str,
        filename: str = "scene.gltf",
        subfolder: Optional[str] = None,
        revision: Optional[str] = None,
        **kwargs,
    ):
        """Load a Scene from a GLTF file on the hub.

        For now the file should be a GLTF-Embedded file (single file) named 'scene.gltf' at the root of the repo.
        """
        gltf_file = hf_hub_download(
            repo_id=repo_id, filename=filename, subfolder=subfolder, revision=revision, repo_type="space"
        )
        nodes = load_gltf_as_tree(gltf_file, repo_id=repo_id, subfolder=subfolder, revision=revision)
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
            created_from_file=gltf_file,
            **kwargs,
        )

    def push_to_hub(self, repo_id: str, local_dir: str, **kwargs):
        """Push a GLTF Scene to the hub.

        For now the file should be a GLTF-Embedded file (single file) named 'scene.gltf' at the root of the repo.
        """
        local_repository = Repository(local_dir=local_dir, clone_from=repo_id, repo_type="space", **kwargs)
        with local_repository.commit("updating scene file"):
            self.save_to_gltf_file("scene.gltf")

    @classmethod
    def load_from_gltf_file(cls, file_path: str, file_type: Optional[str] = None, **kwargs):
        """Load a Scene from a GLTF file."""
        nodes = load_gltf_as_tree(file_path, file_type=file_type)
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
            created_from_file=file_path,
            **kwargs,
        )

    def save_to_gltf_file(self, file_path: str, file_type: Optional[str] = None, **kwargs):
        """Save a Scene from a GLTF file."""
        save_as_gltf_file(file_path, self)

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
        return self._get_decendants_of_class_type(sm.RL_Agent)

    def show(self, in_background: Optional[bool] = None, **engine_kwargs):
        """Render the Scene using the engine if provided."""
        if self.engine is None:
            raise UnsetRendererError()

        self.engine.show(in_background=in_background, **engine_kwargs)
        self._built = True

    def step(self, action):
        """Step the Scene using the engine if provided."""

        if not self._built:
            raise SceneNotBuiltError()

        if self.engine is None:
            raise UnsetRendererError()

        obs = self.engine.step(action)

        return obs

    def __repr__(self):
        return f"Scene(dimensionality={self.dimensionality}, engine='{self.engine}')\n{RenderTree(self).print_tree()}"

    def close(self):
        self.engine.close()
