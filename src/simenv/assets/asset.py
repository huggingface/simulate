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
""" A simenv Asset - Objects in the scene (mesh, primitives, camera, lights)."""
import itertools
import os
import tempfile
import uuid
from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np
from huggingface_hub import create_repo, hf_hub_download, upload_file

from .anytree import NodeMixin, RenderTree
from .collider import Collider
from .utils import camelcase_to_snakecase, get_transform_from_trs, quat_from_euler


if TYPE_CHECKING:
    from ..rl.components import RlComponent


class Asset(NodeMixin, object):
    """Create an Asset in the Scene.

    Parameters
    ----------

    Returns
    -------

    Examples
    --------

    """

    dimensionality = 3  # 2 for bi-dimensional assets and 3 for tri-dimensional assets (default is 3)
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name=None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        transformation_matrix=None,
        collider: Optional[Collider] = None,
        rl_component: Optional["RlComponent"] = None,
        parent=None,
        children=None,
    ):
        self._uuid = uuid.uuid4()
        id = next(getattr(self.__class__, f"_{self.__class__.__name__}__NEW_ID"))
        if name is None:
            name = camelcase_to_snakecase(self.__class__.__name__ + f"_{id:02d}")
        self.name = name

        self.tree_parent = parent
        if children:
            self.tree_children = children

        self._position = None
        self._rotation = None
        self._scaling = None
        self._transformation_matrix = None
        self.position = position
        self.rotation = rotation
        self.scaling = scaling
        if transformation_matrix is not None:
            self.transformation_matrix = transformation_matrix

        self.collider = collider
        self._rl_component = rl_component
        self._n_copies = 0

    @property
    def uuid(self):
        """A unique identifier of the node if needed."""
        return self._uuid

    @property
    def rl_component(self):
        return self._rl_component

    @rl_component.setter
    def rl_component(self, rl_component: "RlComponent"):
        self._rl_component = rl_component
        if rl_component is not None:
            self.action_space = rl_component.action_space
            self.observation_space = rl_component.observation_space
        else:
            self.action_space = None
            self.observation_space = None

    def get(self, name: str):
        """Return the first children tree node with the given name."""
        for node in self.tree_children:
            if node.name == name:
                return node

    def copy(self, with_children=True, **kwargs):
        """Return a copy of the Asset. Parent and children are not attached to the copy."""

        copy_name = self.name + f"_copy{self._n_copies}"
        self._n_copies += 1
        instance_copy = type(self)(
            name=copy_name,
            position=self.position,
            rotation=self.rotation,
            scaling=self.scaling,
            collider=self.collider,
        )

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children

            for child in instance_copy.tree_children:
                child._post_copy()

        return instance_copy

    def _post_copy(self):
        return

    def _get_last_copy_name(self):
        assert self._n_copies > 0, "this object is yet to be copied"
        return self.name + f"_copy{self._n_copies-1}"

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
        # We import dynamically here to avoid circular import (tried many other options...)
        from .gltf_import import load_gltf_as_tree

        if os.path.exists(hub_or_local_filepath) and os.path.isfile(hub_or_local_filepath) and is_local is not False:
            gltf_file = hub_or_local_filepath
        else:
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
                # force_download=True,  # Remove when this is solved: https://github.com/huggingface/huggingface_hub/pull/801#issuecomment-1134576435
                **kwargs,
            )
        nodes = Asset.create_from(gltf_file, repo_id=repo_id, subfolder=subfolder, revision=revision)

        nodes = load_gltf_as_tree(
            gltf_file=gltf_file, file_type=file_type, repo_id=repo_id, subfolder=subfolder, revision=revision
        )
        if len(nodes) == 1:
            root = nodes[0]  # If we have a single root node in the GLTF, we use it for our scene
        else:
            root = Asset(name="Scene", children=nodes)  # Otherwise we build a main root node
        return root

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
    ) -> "Asset":
        """Load a Scene or Asset from the HuggingFace hub or from a local GLTF file.

        First argument is either:
        - a file path on the HuggingFace hub ("USER_OR_ORG/REPO_NAME/PATHS/FILENAME")
        - or a path to a local file on the drive.

        When conflicting files on both, priority is given to the local file (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.load('simenv-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.load('~/documents/gltf-files/scene.gltf'): a local files in user home
        """
        root_node, gltf_file = Asset._get_node_tree_from_hub_or_local(
            hub_or_local_filepath=hub_or_local_filepath,
            use_auth_token=use_auth_token,
            revision=revision,
            is_local=is_local,
            **(hf_hub_kwargs if hf_hub_kwargs is not None else {}),
        )
        return cls(
            name=root_node.name,
            position=root_node.position,
            rotation=root_node.rotation,
            scaling=root_node.scaling,
            children=root_node.tree_children,
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
    ) -> "Asset":
        """Load a Scene from the HuggingFace hub or from a local GLTF file.

        First argument is either:
        - a file path on the HuggingFace hub ("USER_OR_ORG/REPO_NAME/PATHS/FILENAME")
        - or a path to a local file on the drive.

        When conflicting files on both, priority is given to the local file (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.load('simenv-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.load('~/documents/gltf-files/scene.gltf'): a local files in user home
        """
        root_node, gltf_file = Asset._get_node_tree_from_hub_or_local(
            hub_or_local_filepath=hub_or_local_filepath,
            use_auth_token=use_auth_token,
            revision=revision,
            is_local=is_local,
            **kwargs,
        )

        self.clear()
        self.name = root_node.name
        self.position = root_node.position
        self.rotation = root_node.rotation
        self.scaling = root_node.scaling
        self.tree_children = root_node.tree_children
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

    def save(self, file_path: str) -> List[str]:
        """Save in a GLTF file + additional (binary) ressource files if if shoulf be the case.
        Return the list of all the path to the saved files (glTF file + ressource files)
        """
        # We import here to avoid circular deps
        from .gltf_export import save_tree_to_gltf_file

        return save_tree_to_gltf_file(file_path=file_path, root_node=self)

    def as_glb_bytes(self) -> bytes:
        # We import here to avoid circular deps
        from .gltf_export import tree_as_glb_bytes

        return tree_as_glb_bytes(self)

    def translate(self, vector: Optional[List[float]] = None):
        """Translate the asset from a given translation vector

        Parameters
        ----------
        vector : np.ndarray or list, optional
            Translation vector to apply to the object ``[x, y, z]``.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        if vector is None:
            return self
        self.position += np.array(vector)
        return self

    def translate_x(self, amount: Optional[float] = 0.0):
        """Translate the asset along the ``x`` axis of the given amount

        Parameters
        ----------
        amount : float, optional
            Amount to translate the asset along the ``x`` axis.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        self.position += np.array((float(amount), 0.0, 0.0))
        return self

    def translate_y(self, amount: Optional[float] = 0.0):
        """Translate the asset along the ``y`` axis of the given amount

        Parameters
        ----------
        amount : float, optional
            Amount to translate the asset along the ``y`` axis.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        self.position += np.array((0.0, float(amount), 0.0))
        return self

    def translate_z(self, amount: Optional[float] = 0.0):
        """Translate the asset along the ``z`` axis of the given amount

        Parameters
        ----------
        amount : float, optional
            Amount to translate the asset along the ``z`` axis.
            Default to applying no translation.

        Returns
        -------
        self : Asset modified in-place with the translation.

        Examples
        --------

        """
        self.position += np.array((0.0, 0.0, float(amount)))
        return self

    def rotate(self, rotation: Optional[List[float]] = None):
        """Rotate the asset with a given rotation quaternion.
        Use ``rotate_x``, ``rotate_y`` or ``rotate_z`` for simple rotations around a specific axis.

        Parameters
        ----------
        rotation : np.ndarray or list, optional
            Rotation quaternion to apply to the object ``[x, y, z, w]``.
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        if rotation is None:
            return self
        self.rotation = np.array(rotation) * self.rotation
        return self

    def _rotate_axis(self, vector: Optional[List[float]] = None, value: Optional[float] = None):
        """Helper to rotate around a single axis."""
        if value is None or vector is None:
            return self
        self.rotation = np.array(vector + [np.radians(value)]) * self.rotation
        return self

    def rotate_x(self, value: Optional[float] = None):
        """Rotate the asset around the ``x`` axis with a given rotation value in degree.

        Parameters
        ----------
        rotation : float, optional
            Rotation value to apply to the object around the ``x`` axis in degree .
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        return self._rotate_axis(vector=[1.0, 0.0, 0.0], value=value)

    def rotate_y(self, value: Optional[float] = None):
        """Rotate the asset around the ``y`` axis with a given rotation value in degree.

        Parameters
        ----------
        rotation : float, optional
            Rotation value to apply to the object around the ``y`` axis in degree .
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        return self._rotate_axis(vector=[0.0, 1.0, 0.0], value=value)

    def rotate_z(self, value: Optional[float] = None):
        """Rotate the asset around the ``z`` axis with a given rotation value in degree.

        Parameters
        ----------
        rotation : float, optional
            Rotation value to apply to the object around the ``z`` axis in degree .
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        return self._rotate_axis(vector=[0.0, 0.0, 1.0], value=value)

    def scale(self, scaling: Optional[Union[float, List[float]]] = None):
        """Scale the asset with a given scaling, either a global scaling value or a vector of ``[x, y, z]`` scaling values.
        Use ``scale_x``, ``scale_y`` or ``scale_z`` for simple scaling around a specific axis.

        Parameters
        ----------
        scaling : float or np.ndarray or list, optional
            Global scaling (float) or vector of  scaling values to apply to the object along the ``[x, y, z]`` axis.
            Default to applying no scaling.

        Returns
        -------
        self : Asset modified in-place with the scaling.

        Examples
        --------

        """
        if scaling is None:
            return self
        if scaling is None:
            scaling = [1.0, 1.0, 1.0]
        elif isinstance(scaling, (float, int)) or (isinstance(scaling, np.ndarray) and len(scaling) == 1):
            scaling = [scaling, scaling, scaling]
        elif len(scaling) != 3:
            raise ValueError("Scale should be of size 1 (Uniform scale) or 3 (X, Y, Z)")
        self.scaling = np.multiply(self.scaling, scaling)
        return self

    def scale_x(self, value: Optional[float] = None):
        """scale the asset around the ``x`` axis with a given scaling value.

        Parameters
        ----------
        value : float, optional
            scaling value to apply to the object around the ``x`` axis.
            Default to applying no scaling.

        Returns
        -------
        self : Asset modified in-place with the scaling.

        Examples
        --------

        """

        return self.scale(vector=[1.0, 0.0, 0.0], value=value)

    def scale_y(self, value: Optional[float] = None):
        """scale the asset around the ``y`` axis with a given scaling value.

        Parameters
        ----------
        value : float, optional
            scaling value to apply to the object around the ``y`` axis .
            Default to applying no scaling.

        Returns
        -------
        self : Asset modified in-place with the scaling.

        Examples
        --------

        """

        return self.scale(vector=[0.0, 1.0, 0.0], value=value)

    def scale_z(self, value: Optional[float] = None):
        """scale the asset around the ``z`` axis with a given value.

        Parameters
        ----------
        value : float, optional
            Scale value to apply to the object around the ``z`` axis.
            Default to applying no scaling.

        Returns
        -------
        self : Asset modified in-place with the scaling.

        Examples
        --------

        """

        return self.scale(vector=[0.0, 0.0, 1.0], value=value)

    # getters for position/rotation/scale

    @property
    def position(self):
        return self._position

    @property
    def rotation(self):
        return self._rotation

    @property
    def scaling(self):
        return self._scaling

    @property
    def transformation_matrix(self):
        if self._transformation_matrix is None:
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
        return self._transformation_matrix

    # setters for position/rotation/scale

    @position.setter
    def position(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0]
            elif len(value) != 3:
                raise ValueError("position should be of size 3 (X, Y, Z)")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._position = np.array(value)
        self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

        if getattr(self.tree_root, "engine", None) is not None:
            self.tree_root.engine.update_asset(self)

    @rotation.setter
    def rotation(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0, 1.0]
            elif len(value) == 3:
                value = quat_from_euler(*value)
            elif len(value) != 4:
                raise ValueError("rotation should be of size 3 (Euler angles) or 4 (Quaternions")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._rotation = np.array(value)
        self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

        if getattr(self.tree_root, "engine", None) is not None:
            self.tree_root.engine.update_asset(self)

    @scaling.setter
    def scaling(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [1.0, 1.0, 1.0]
            elif len(value) == 1:
                value = [value, value, value]
            elif len(value) != 3:
                raise ValueError("Scale should be of size 1 (Uniform scale) or 3 (X, Y, Z)")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._scaling = np.array(value)
        self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

        if getattr(self.tree_root, "engine", None) is not None:
            self.tree_root.engine.update_asset(self)

    @transformation_matrix.setter
    def transformation_matrix(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._transformation_matrix = np.array(value)

        # Not sure we can extract position/rotation/scale from transform matrix in a unique way
        # Reset position/rotation/scale
        self._position = None
        self._rotation = None
        self._scaling = None

        self._post_asset_modification()

    def _post_asset_modification(self):
        if getattr(self.tree_root, "engine", None) is not None and self.tree_root.tree_root.engine.auto_update:
            self.tree_root.engine.update_asset(self)

    def _post_attach_parent(self, parent):
        """NodeMixing nethod call after attaching to a `parent`."""
        if getattr(parent.tree_root, "engine", None) is not None and parent.tree_root.engine.auto_update:
            parent.tree_root.engine.update_asset(self)

    def _post_detach_parent(self, parent):
        """NodeMixing nethod call after detaching from a `parent`."""
        if getattr(parent.tree_root, "engine", None) is not None and parent.tree_root.engine.auto_update:
            parent.tree_root.engine.remove_asset(self)
