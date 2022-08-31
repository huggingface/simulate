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
from typing import Any, List, Optional, Tuple, Union

import numpy as np
from huggingface_hub import create_repo, hf_hub_download, upload_file

from .anytree import NodeMixin, TreeError
from .articulated_body import ArticulatedBodyComponent
from .controller import Controller, ControllerDict, ControllerTuple
from .rigid_body import RigidBodyComponent
from .utils import (
    camelcase_to_snakecase,
    get_product_of_quaternions,
    get_transform_from_trs,
    get_trs_from_transform_matrix,
    rotation_from_euler_degrees,
)


ALLOWED_COMPONENTS_ATTRIBUTES = ["actuator", "physics_component"]


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
        controller: Optional[Union[Controller, ControllerDict, ControllerTuple]] = None,
        physics_component: Union[None, RigidBodyComponent, ArticulatedBodyComponent] = None,
        parent=None,
        children=None,
        created_from_file=None,
    ):
        self._uuid = uuid.uuid4()
        id = next(getattr(self.__class__, f"_{self.__class__.__name__}__NEW_ID"))
        if name is None:
            name = camelcase_to_snakecase(self.__class__.__name__ + f"_{id:02d}")
        self.name = name

        self.tree_parent = parent
        if children is not None:
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

        # Extensions for physics/RL
        self.controller = controller
        self.physics_component = physics_component

        self._n_copies = 0
        self._created_from_file = created_from_file

    @property
    def uuid(self):
        """A unique identifier of the node if needed."""
        return self._uuid

    @property
    def named_components(self) -> List[Tuple[str, Any]]:
        """Return a list of the components of the asset with their attributes name.

        We strip the beginning "_" of the attribute names (if stored as private).
        """
        for attribute in ALLOWED_COMPONENTS_ATTRIBUTES:
            if getattr(self, attribute, None) is not None:
                yield (attribute, getattr(self, attribute))

    @property
    def components(self) -> List[Any]:
        """Return a list of the components of the asset."""
        return list(comp for _, comp in self.named_components)

    # Actions and action_space
    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller: Union[Controller, ControllerTuple, ControllerDict]):
        self._controller = controller

    @property
    def action_space(self):
        if self.controller is not None:
            return self.controller.space
        return None

    @property
    def physics_component(self):
        return self._physics_component

    @physics_component.setter
    def physics_component(self, physics_component: Union[None, RigidBodyComponent, ArticulatedBodyComponent]):
        self._physics_component = physics_component

    def __len__(self):
        return len(self.tree_descendants)

    def get_node(self, name: str) -> Optional["Asset"]:
        """Return the node with the given name in the *whole* tree.
        (Remember that the name of the nodes are unique)

        Return None if no node with the given name is found.
        """
        for node in self.tree_root.tree_descendants:
            if node.name == name:
                return node
        return None

    def copy(self, with_children=True, **kwargs):
        """Return a copy of the Asset. Parent and children are not attached to the copy."""

        copy_name = self.name + f"_copy{self._n_copies}"
        self._n_copies += 1
        instance_copy = type(self)(
            name=copy_name,
            position=self.position,
            rotation=self.rotation,
            scaling=self.scaling,
        )

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children

            for child in instance_copy.tree_children:
                child._post_copy()

        return instance_copy

    def clear(self):
        """Remove all assets in the scene or children to the asset."""
        self.tree_children = []
        return self

    def _post_copy(self):
        pass

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
    ) -> Tuple["Asset", str]:
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

        repo_id = None
        subfolder = None

        if os.path.exists(hub_or_local_filepath) and os.path.isfile(hub_or_local_filepath) and is_local is not False:
            file_path = hub_or_local_filepath
        else:
            splitted_hub_path = hub_or_local_filepath.split("/")
            repo_id = splitted_hub_path[0] + "/" + splitted_hub_path[1]

            filename = splitted_hub_path[-1]
            filename_extension = filename.split(".")
            if len(filename_extension) == 1:
                filename += ".gltf"

            subfolder = "/".join(splitted_hub_path[2:-1])

            file_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                subfolder=subfolder
                if subfolder
                else None,  # remove when https://github.com/huggingface/huggingface_hub/issues/1016
                revision=revision,
                repo_type="space",
                use_auth_token=use_auth_token,
                **kwargs,
            )

        nodes = load_gltf_as_tree(
            file_path=file_path, file_type=file_type, repo_id=repo_id, subfolder=subfolder, revision=revision
        )
        if len(nodes) == 1:
            root = nodes[0]  # If we have a single root node in the GLTF, we use it for our scene
        else:
            root = Asset(name="Scene", children=nodes)  # Otherwise we build a main root node

        return root, file_path

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

        hub_filename_extension = hub_filename.split(".")
        if len(hub_filename_extension) == 1:
            hub_filename += ".gltf"

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

    def rotate_by_quaternion(self, quaternion: Optional[List[float]] = None):
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
        if quaternion is None:
            return self
        if len(quaternion) != 4:
            raise ValueError("Rotation quaternion must be of length 4")
        normalized_quaternion = np.array(quaternion) / np.linalg.norm(quaternion)
        self.rotation = get_product_of_quaternions(normalized_quaternion, self.rotation)
        return self

    def rotate_around_vector(self, vector: Optional[List[float]] = None, value: Optional[float] = None):
        """Rotate around a vector from a specific amount.
        Use ``rotate_x``, ``rotate_y`` or ``rotate_z`` for simple rotations around a specific axis.

        Parameters
        ----------
        vector : np.ndarray or list, optional
            Vector to rotate around.

        value : float, optional
            Rotation value in degree to apply to the object around the vector.
            Default to applying no rotation.

        Returns
        -------
        self : Asset modified in-place with the rotation.

        Examples
        --------

        """
        if value is None or vector is None:
            return self
        if len(vector) != 3:
            raise ValueError("Vector must be a 3D vector")
        radian_value = np.radians(value) / 2  # We use value/2 in radian in the quaternion values
        normalized_vector = np.array(vector) / np.linalg.norm(vector)
        new_rotation = np.append(normalized_vector * np.sin(radian_value), np.cos(radian_value))
        self.rotation = get_product_of_quaternions(new_rotation, self.rotation)
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
        return self.rotate_around_vector(vector=[1.0, 0.0, 0.0], value=value)

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
        return self.rotate_around_vector(vector=[0.0, 1.0, 0.0], value=value)

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
        return self.rotate_around_vector(vector=[0.0, 0.0, 1.0], value=value)

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
                value = rotation_from_euler_degrees(*value)
            elif len(value) != 4:
                raise ValueError("rotation should be of size 3 (Euler angles) or 4 (Quaternions")
            else:
                value = [float(v) for v in value]
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._rotation = np.array(value) / np.linalg.norm(value)
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

        translation, rotation, scale = get_trs_from_transform_matrix(value)
        self._position = translation
        self._rotation = rotation
        self._scaling = scale

        self._post_asset_modification()

    def _post_asset_modification(self):
        if getattr(self.tree_root, "engine", None) is not None and self.tree_root.tree_root.engine.auto_update:
            self.tree_root.engine.update_asset(self)

    def _post_attach_parent(self, parent):
        """NodeMixing nethod call after attaching to a `parent`."""
        parent.tree_root._check_all_names_unique()  # Check that all names are unique in the tree
        if getattr(parent.tree_root, "engine", None) is not None:
            if parent.tree_root.engine.auto_update:
                parent.tree_root.engine.update_asset(self)

        # We have a couple of restrictions on parent/children nodes

        # Avoid circular imports (Reward functions are Asset) - unfortunately we cannot do this test on the Reward function side
        # as this would involve calling _post_attaching_childran
        from .collider import Collider
        from .reward_functions import RewardFunction

        if isinstance(parent, RewardFunction):
            if not isinstance(self, RewardFunction):
                raise TreeError(
                    f"Reward functions can only have reward function as children. "
                    f"You are trying to make node {self.name} of type {type(self)} "
                    f"a child of node {parent.name} of type {type(parent)}"
                )
        elif isinstance(parent, Collider):
            raise TreeError(
                f"Colliders can not have children. "
                f"You are trying to make node {self.name} of type {type(self)} "
                f"a child of node {parent.name} of type {type(parent)}"
            )

    def _post_detach_parent(self, parent):
        """NodeMixing nethod call after detaching from a `parent`."""
        if getattr(parent.tree_root, "engine", None) is not None and parent.tree_root.engine.auto_update:
            parent.tree_root.engine.remove_asset(self)

    def _post_name_change(self, value):
        """NodeMixing nethod call after changing the name of a node."""
        self.tree_root._check_all_names_unique()  # Check that all names are unique in the tree

    def _check_all_names_unique(self):
        """Check that all names are unique in the tree."""
        seen = set()  # O(1) lookups
        for node in self.tree_descendants:
            if node.name not in seen:
                seen.add(node.name)
            else:
                raise ValueError("Node name '{}' is not unique".format(node.name))
