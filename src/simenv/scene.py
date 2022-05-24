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
from fileinput import filename
from typing import List, Optional

from huggingface_hub import create_repo, hf_hub_download, logging, upload_file
from isort import file

import simenv as sm

from .assets import Asset
from .assets.anytree import RenderTree
from .engine import PyVistaEngine, UnityEngine
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
    def load(
        cls,
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
        if os.path.exists(hub_or_local_filepath) and os.path.isfile(hub_or_local_filepath) and not is_local is False:
            return cls.load_from_file(filepath=hub_or_local_filepath, **kwargs)

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

    @classmethod
    def load_from_file(cls, filepath: str, file_type: Optional[str] = None, **kwargs) -> "Scene":
        """Load a Scene from a GLTF file."""
        nodes = load_gltf_as_tree(filepath, file_type=file_type)
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
            created_from_file=filepath,
            **kwargs,
        )

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
