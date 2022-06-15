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
import os
import tempfile
from typing import List, Optional, Union

from huggingface_hub import create_repo, hf_hub_download, logging, upload_file

import simenv as sm

from .assets import Asset
from .assets.anytree import RenderTree
from .engine import GodotEngine, PyVistaEngine, UnityEngine
from .gltf_export import save_tree_as_gltf_file
from .gltf_import import load_gltf_as_tree


# Set Hugging Face hub debug verbosity (TODO remove)
logging.set_verbosity_debug()


class UnsetRendererError(Exception):
    pass


class SceneNotBuiltError(Exception):
    pass


class Scene(Asset):
    def __init__(
        self,
        engine: Optional[str] = "pyvista",
        name: Optional[str] = None,
        created_from_file: Optional[str] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        transformation_matrix=None,
        children=None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            transformation_matrix=transformation_matrix,
            children=children,
        )
        self.engine = None
        self._built = False
        self._created_from_file = created_from_file
        if engine is not None:
            engine = engine.lower()
        if engine == "unity":
            self.engine = UnityEngine(self, **kwargs)
        elif engine == "godot":
            self.engine = GodotEngine(self)
        elif engine == "blender":
            raise NotImplementedError()
        elif engine == "pyvista" or engine is None:
            self.engine = PyVistaEngine(self, **kwargs)
        elif engine is not None:
            raise ValueError("engine should be selected in the list [None, 'unity', 'blender', 'pyvista']")

    @staticmethod
    def _get_node_tree_from_hub_or_local(
        hub_or_local_filepath: str,
        use_auth_token: Optional[str] = None,
        revision: Optional[str] = None,
        is_local: Optional[bool] = None,
        file_type: Optional[str] = None,
        **kwargs,
    ):
        """Return a root tree loaded from the HuggingFace hub or from a local GLTF file.

        First argument is either:
        - a file path on the HuggingFace hub ("USER_OR_ORG/REPO_NAME/PATHS/FILENAME")
        - or a path to a local file on the drive.

        When conflicting files on both, priority is given to the local file (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.load('simenv-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.load('~/documents/gltf-files/scene.gltf'): a local files in user home
        """
        if os.path.exists(hub_or_local_filepath) and os.path.isfile(hub_or_local_filepath) and is_local is not False:
            nodes = load_gltf_as_tree(hub_or_local_filepath, file_type=file_type)
            return nodes, hub_or_local_filepath

        splitted_hub_path = hub_or_local_filepath.split("/")
        repo_id = splitted_hub_path[0] + "/" + splitted_hub_path[1]
        filename = splitted_hub_path[-1]
        subfolder = "/".join(splitted_hub_path[2:-1])
        gltf_file = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            subfolder=subfolder,
            revision=revision,
            repo_type="space",
            use_auth_token=use_auth_token,
            force_download=True,  # Remove when this is solved: https://github.com/huggingface/huggingface_hub/pull/801#issuecomment-1134576435
            **kwargs,
        )
        nodes = load_gltf_as_tree(gltf_file, repo_id=repo_id, subfolder=subfolder, revision=revision)
        return nodes, gltf_file

    @classmethod
    def create_from(
        cls,
        hub_or_local_filepath: str,
        use_auth_token: Optional[str] = None,
        revision: Optional[str] = None,
        is_local: Optional[bool] = None,
        hf_hub_kwargs: Optional[dict] = None,
        **kwargs,
    ) -> "Scene":
        """Load a Scene from the HuggingFace hub or from a local GLTF file.

        First argument is either:
        - a file path on the HuggingFace hub ("USER_OR_ORG/REPO_NAME/PATHS/FILENAME")
        - or a path to a local file on the drive.

        When conflicting files on both, priority is given to the local file (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.load('simenv-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.load('~/documents/gltf-files/scene.gltf'): a local files in user home
        """
        nodes, gltf_file = Scene._get_node_tree_from_hub_or_local(
            hub_or_local_filepath=hub_or_local_filepath,
            use_auth_token=use_auth_token,
            revision=revision,
            is_local=is_local,
            **(hf_hub_kwargs if hf_hub_kwargs is not None else {}),
        )
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

    def load(
        self,
        hub_or_local_filepath: str,
        use_auth_token: Optional[str] = None,
        revision: Optional[str] = None,
        is_local: Optional[bool] = None,
        **kwargs,
    ) -> "Scene":
        """Load a Scene from the HuggingFace hub or from a local GLTF file.

        First argument is either:
        - a file path on the HuggingFace hub ("USER_OR_ORG/REPO_NAME/PATHS/FILENAME")
        - or a path to a local file on the drive.

        When conflicting files on both, priority is given to the local file (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.load('simenv-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.load('~/documents/gltf-files/scene.gltf'): a local files in user home
        """
        nodes, gltf_file = Scene._get_node_tree_from_hub_or_local(
            hub_or_local_filepath=hub_or_local_filepath,
            use_auth_token=use_auth_token,
            revision=revision,
            is_local=is_local,
            **kwargs,
        )

        if len(nodes) == 1:
            root = nodes[0]  # If we have a single root node in the GLTF, we use it for our scene
            nodes = root.tree_children
        else:
            root = Asset(name="Scene")  # Otherwise we build a main root node

        self.clear()
        self.name = root.name
        self.position = root.position
        self.rotation = root.rotation
        self.scaling = root.scaling
        self.tree_children = nodes
        self.created_from_file = gltf_file

    def push_to_hub(
        self,
        hub_filepath: str,
        token: Optional[str] = None,
        revision: Optional[str] = None,
        identical_ok: bool = True,
        private: bool = False,
        **kwargs,
    ) -> List[str]:
        """Push a GLTF Scene to the hub.

        First argument is a file path on the HuggingFace hub ("USER_OR_ORG/REPO_NAME/PATHS/FILENAME")
        Return the url on the hub of the file.

        Example:
        - scene.push_to_hub('simenv-tests/Box/glTF-Embedded/Box.gltf')
        """
        splitted_hub_path = hub_filepath.split("/")
        hub_repo_id = splitted_hub_path[0] + "/" + splitted_hub_path[1]
        hub_filename = splitted_hub_path[-1]
        hub_subfolder = "/".join(splitted_hub_path[2:-1])

        repo_url = create_repo(
            repo_id=hub_repo_id,
            token=token,
            private=private,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=identical_ok,
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            full_filename = os.path.join(tmpdirname, hub_filename)
            saved_filepaths = self.save(full_filename)
            hub_urls = []
            for saved_filepath in saved_filepaths:
                saved_filename = os.path.basename(saved_filepath)
                repo_filepath = os.path.join(hub_subfolder, saved_filename)
                hub_url = upload_file(
                    path_or_fileobj=saved_filepath,
                    path_in_repo=repo_filepath,
                    repo_id=hub_repo_id,
                    token=token,
                    repo_type="space",
                    revision=revision,
                    identical_ok=identical_ok,
                )
                hub_urls.append(hub_url)
        return repo_url

    def save(self, filepath: str, **kwargs) -> List[str]:
        """Save a Scene as a GLTF file (with optional ressources in the same folder)."""
        return save_tree_as_gltf_file(filepath, self)

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

    def show(self, **engine_kwargs):
        """Render the Scene using the engine if provided."""
        if self.engine is None:
            raise UnsetRendererError()

        self.engine.show(**engine_kwargs)
        self._built = True

    def _check_backend(self):
        if not self._built:
            raise SceneNotBuiltError()
        if self.engine is None:
            raise UnsetRendererError()

    def reset(self):
        """Reset the environment / episode"""
        self._check_backend()
        return self.engine.reset()

    def get_done(self):
        """Find out if the episode has ended"""
        self._check_backend()
        return self.engine.get_done()

    def get_reward(self):
        """Get the reward from the agent"""
        self._check_backend()
        return self.engine.get_reward()

    def step(self, action):
        """Step the Scene using the engine if provided."""
        self._check_backend()
        return self.engine.step(action)

    def get_observation(self):
        """Step the Scene using the engine if provided."""
        self._check_backend()
        return self.engine.get_observation()

    def __len__(self):
        return len(self.tree_descendants)

    def __repr__(self):
        return f"Scene(dimensionality={self.dimensionality}, engine='{self.engine}')\n{RenderTree(self).print_tree()}"

    def close(self):
        self.engine.close()
