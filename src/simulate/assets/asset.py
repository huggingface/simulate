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
""" A simulate Asset - Objects in the scene (mesh, primitives, camera, lights)."""
import itertools
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from huggingface_hub import create_repo, hf_hub_download, upload_file

from ..utils import logging
from .actuator import Actuator, ActuatorDict, spaces
from .anytree import NodeMixin, TreeError
from .articulation_body import ArticulationBodyComponent
from .rigid_body import RigidBodyComponent
from .utils import (
    camelcase_to_snakecase,
    get_product_of_quaternions,
    get_transform_from_trs,
    get_trs_from_transform_matrix,
    rotation_from_euler_degrees,
)


logger = logging.get_logger(__name__)
ALLOWED_COMPONENTS_ATTRIBUTES = ["actuator", "physics_component", "actuator"]


class Asset(NodeMixin, object):
    """Create an Asset in the Scene.

    Parameters
    ----------
    name : str, optional
        Name of the asset, by default set to [class_name]_[counter]
    position : List[float] (Vector3), optional
        Position of the asset in the scene, by default [0, 0, 0]
    rotation : List[float] (Quaternion), optional
        Rotation of the asset in the scene, by default [0, 0, 0, 1]
    scaling : Union[float, List[float]] (Vector3), optional
        Scaling of the asset in the scene, by default 1
    transformation_matrix : List[float] (Matrix4x4), optional
        Transformation matrix of the asset in the scene, by default computed from position, rotation and scaling
    actuator : Union[Actuator, ActuatorDict], optional
        Actuator to control movements of the asset, by default None.
        Setting an actuator will make the Asset an ``Actor``.$
    physics_component : Union[None, RigidBodyComponent, ArticulationBodyComponent], optional
        Physics component of the asset, by default None
        Setting a physics component will make the Asset move according to the physics engine.
    is_actor : bool, optional
        If True, the asset will be the root node of an actor, by default False.
        This can be used to group a tree of related nodes and actuators in a single
        identified actor in the scene.
    parent : Asset, optional
        Parent of the asset, by default None
    children : List[Asset], optional
        Children of the asset, by default None
    created_from_file : str, optional
        Path to the file from which the asset was created if relevant, by default None

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
        actuator: Optional[Union[Actuator, ActuatorDict]] = None,
        physics_component: Optional[Union[RigidBodyComponent, ArticulationBodyComponent]] = None,
        is_actor: bool = False,
        parent=None,
        children=None,
        created_from_file=None,
    ):
        asset_id = next(getattr(self.__class__, f"_{self.__class__.__name__}__NEW_ID"))
        if name is None:
            name = camelcase_to_snakecase(self.__class__.__name__ + f"_{asset_id:02d}")
        self.name = name

        self.tree_parent = parent
        if children is not None:
            self.tree_children = children

        self.is_actor = is_actor

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
        self.actuator = actuator
        self.physics_component = physics_component

        self._n_copies = 0
        self._created_from_file = created_from_file

    def _repr_info_str(self) -> str:
        """Used to add additional information to the __repr__ method."""
        return ""

    def __repr__(self):
        asset_str = ""
        if self.is_actor:
            asset_str += "is_actor=True, "
        if self.actuator is not None:
            asset_str += f"actuator={self.actuator.__class__.__name__}(), "
        if self.physics_component is not None:
            asset_str += f"physics_component={self.physics_component.__class__.__name__}(), "
        return f"{self.name}: {self.__class__.__name__}({asset_str}{self._repr_info_str()})"

    @property
    def named_components(self) -> List[Tuple[str, Any]]:
        """Return a list of the components of the asset with their attributes name.

        We strip the beginning "_" of the attribute names (if stored as private).
        """
        for attribute in ALLOWED_COMPONENTS_ATTRIBUTES:
            if getattr(self, attribute, None) is not None:
                yield attribute, getattr(self, attribute)

    @property
    def components(self) -> List[Any]:
        """Return a list of the components of the asset."""
        return list(comp for _, comp in self.named_components)

    # Actions and action_space
    @property
    def actuator(self) -> Optional[Union[Actuator, ActuatorDict]]:
        return self._actuator

    @actuator.setter
    def actuator(self, actuator: Optional[Union[Actuator, ActuatorDict]]):
        self._actuator = actuator

    @property
    def physics_component(self):
        return self._physics_component

    def check_parent_physics(self):
        # TODO: replace with tree operations
        if self.tree_parent is not None:
            if self.tree_parent.physics_component is not None:
                return True
            else:
                return self.tree_parent.check_parent_physics()
        return False

    @physics_component.setter
    def physics_component(self, physics_component: Union[None, RigidBodyComponent, ArticulationBodyComponent]):
        self._physics_component = physics_component

        if physics_component is not None:
            # recursively check for parent with physics_component
            multiple_physics = self.check_parent_physics()
            if multiple_physics:
                print("WARNING: A linked child asset and parent asset have a physics component, not supported.")

    @property
    def action_space(self) -> Optional[spaces.Dict]:
        """Build and return the action space of the actor if the asset is an actor (is_actor=True).
        The action space is a space Dict with keys coresponding to the tags of the actuators.
        If some actuators have space Dict action spaces, they are flattened.
        If the returned action space Dict has a single entry, we return the single space instead of the Dict.
        """
        # [The following is NOT implemented at the moment]
        # If the asset has multiple actuators with different ids,
        # actuators of identical types are grouped together by tags and index
        # in particular:
        # - Box actuators will be grouped together in a concatenated Box space along the first axis
        # - Discrete/MultiDiscrete actuators will be grouped together in a MultiDiscrete space
        # - MultiBinary actuators will be grouped together in a larger MultiBinary space
        # Actuators with different tags will be grouped together in a Dict space.

        def update_dict_space(act: Union[Actuator, ActuatorDict], actions_space_dict: Dict[str, spaces.Space]):
            """Helper function to update a Dict space with the action space associated to an actuator."""
            if act is None:
                return
            if isinstance(act, Actuator):
                if act.actuator_tag not in actions_space_dict:
                    actions_space_dict[act.actuator_tag] = act.action_space
                else:
                    raise ValueError(f"Actuator with tag {act.actuator_tag} already exists in the action space. ")
                    # actions_space_dict[act.actuator_tag].append((act.index, act.action_space))
            elif isinstance(act, ActuatorDict):
                for value in act.actuators.values():
                    if value.actuator_tag not in actions_space_dict:
                        actions_space_dict[value.actuator_tag] = value.action_space
                    else:
                        raise ValueError(
                            f"Actuator with tag {value.actuator_tag} already exists in the action space. "
                        )
                        # actions_space_dict[value.actuator_tag].append((value.index, value.action_space))
            else:
                raise NotImplementedError()

        if not self.is_actor:
            return None

        actions_space_dict: Dict[str, spaces.Space] = dict()

        # Let's populate the action space dict with the actuator of the actor root node and of it's descendants
        update_dict_space(self.actuator, actions_space_dict)
        for descendant in self.tree_descendants:
            update_dict_space(descendant.actuator, actions_space_dict)

        # Now let's merge the actions if they share tags
        # merged_dict = dict()
        # for tag, actions in actions_space_dict.items():
        #     actions.sort(key=lambda x: x[0])  # Sort by index
        #     actions = [action for _, action in actions]  # and remove the index
        #     if len(actions) == 0:
        #         continue
        #     elif len(actions) == 1:
        #         merged_dict[tag] = actions[0]
        #     else:
        #         if all(isinstance(act, spaces.Box) for act in actions):
        #             dtype=actions[0].dtype
        #             seed=actions[0].seed
        #             merged_dict[tag] = spaces.Box(
        #                 np.concatenate([act.low for act in actions]),
        #                 np.concatenate([act.high for act in actions]),
        #                 dtype=dtype,
        #                 seed=seed
        #             )
        #         elif all(isinstance(act, spaces.Discrete) for act in actions):
        #             merged_dict[tag] = spaces.MultiDiscrete([act.n for act in actions], seed=seed)
        #         elif all(isinstance(act, spaces.MultiBinary) for act in actions):
        #             merged_dict[tag] = spaces.MultiBinary([act.n for act in actions], seed=seed)
        #         else:
        #             raise ValueError(f"Issue with merging the actions {actions}")

        # if there is only one action space, we return it directly
        if len(actions_space_dict) == 1:
            return actions_space_dict[list(actions_space_dict.keys())[0]]
        else:
            return spaces.Dict(actions_space_dict)

    @property
    def action_tags(self) -> Optional[List[str]]:
        """Return the list of all action tags of the actor (keys of the action_space)."""

        def update_tag_list(act: Union[Actuator, ActuatorDict], tag_list: List[str]):
            """Helper function to update a list of all the action tags."""
            if act is None:
                return
            if isinstance(act, Actuator):
                if act.actuator_tag not in tag_list:
                    tag_list.append(act.actuator_tag)
                else:
                    raise ValueError(f"Actuator with tag {act.actuator_tag} already exists in the action space. ")
            elif isinstance(act, ActuatorDict):
                for value in act.actuators.values():
                    if value.actuator_tag not in tag_list:
                        tag_list.append(value.actuator_tag)
                    else:
                        raise ValueError(
                            f"Actuator with tag {value.actuator_tag} already exists in the action space. "
                        )
            else:
                raise NotImplementedError()

        if not self.is_actor:
            return None
        else:
            tag_list: List[str] = []

            # Let's populate the action tag list with the actuator of the actor root node and of it's descendants
            update_tag_list(self.actuator, tag_list)
            for descendant in self.tree_descendants:
                update_tag_list(descendant.actuator, tag_list)

            return tag_list

    @property
    def observation_space(self) -> Optional[spaces.Space]:
        if not self.is_actor:
            return None
        else:
            sensors = self.tree_filtered_descendants(lambda node: getattr(node, "sensor_tag", None) is not None)
            return spaces.Dict({sensor.sensor_tag: sensor.observation_space for sensor in sensors})

    @property
    def sensor_tags(self) -> Optional[List[str]]:
        if not self.is_actor:
            return None

        sensors = self.tree_filtered_descendants(lambda node: getattr(node, "sensor_tag", None) is not None)

        return [sensor.sensor_tag for sensor in sensors]

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

        When conflicting files on both, priority is given to the local file
        (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.create_from('simulate-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.create_from('~/documents/gltf-files/scene.gltf'): a local files in user home
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

            # remove when release with https://github.com/huggingface/huggingface_hub/pull/1021 is out
            subfolder = subfolder if subfolder else None
            file_path = ""
            try:
                file_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    subfolder=subfolder,
                    revision=revision,
                    repo_type="dataset",
                    use_auth_token=use_auth_token,
                    **kwargs,
                )
            except Exception as e:
                logger.info("Could not load Asset from Datasets:", e)

            if not file_path:
                try:
                    file_path = hf_hub_download(
                        repo_id=repo_id,
                        filename=filename,
                        subfolder=subfolder,
                        revision=revision,
                        repo_type="space",
                        use_auth_token=use_auth_token,
                        **kwargs,
                    )
                except Exception as e:
                    raise RuntimeError("Could not load Asset from Spaces:", e)

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

        When conflicting files on both, priority is given to the local file
        (use 'is_local=True/False' to force from the Hub or from local file)

        Examples:
        - Scene.create_from('simulate-tests/Box/glTF-Embedded/Box.gltf'): a file on the hub
        - Scene.create_from('~/documents/gltf-files/scene.gltf'): a local files in user home
        """
        root_node, gltf_file = Asset._get_node_tree_from_hub_or_local(
            hub_or_local_filepath=hub_or_local_filepath,
            use_auth_token=use_auth_token,
            revision=revision,
            is_local=is_local,
            **(hf_hub_kwargs if hf_hub_kwargs is not None else {}),
        )

        root_node.name = kwargs.pop("name", root_node.name)
        root_node.position = kwargs.pop("position", root_node.position)
        root_node.rotation = kwargs.pop("rotation", root_node.rotation)
        root_node.scaling = kwargs.pop("scaling", root_node.scaling)

        for node in root_node.tree_children:
            node.name = root_node.name + "_" + node.name

        return cls(
            name=root_node.name,
            position=root_node.position,
            rotation=root_node.rotation,
            scaling=root_node.scaling,
            children=root_node.tree_children,
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
        - scene.push_to_hub('simulate-tests/Box/glTF-Embedded/Box.gltf')
        """
        split_hub_path = hub_filepath.split("/")
        hub_repo_id = split_hub_path[0] + "/" + split_hub_path[1]
        hub_filename = split_hub_path[-1]
        hub_subfolder = "/".join(split_hub_path[2:-1])

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
        """Save in a GLTF file + additional (binary) resource files if it should be the case.
        Return the list of all the path to the saved files (glTF file + resource files)
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
        quaternion : np.ndarray or list, optional
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
        value : float, optional
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
        value : float, optional
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
        value : float, optional
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
        """Scale the asset with a given scaling, either a global scaling value
        or a vector of ``[x, y, z]`` scaling values.
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

    ##############################
    # Properties copied from Asset()
    # We need to redefine them here otherwise the dataclass lose them since
    # they are also in the __init__ signature
    #
    # Need to be updated if Asset() is updated
    ##############################
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
            if value is None or isinstance(value, property):
                value = [0.0, 0.0, 0.0]
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) != 3:
                raise ValueError("position should be of size 3 (X, Y, Z)")
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
                value = [float(v) for v in value]
            else:
                raise TypeError("Position must be a list of 3 numbers")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_position = np.array(value)
        if not np.array_equal(self._position, new_position):
            self._position = new_position
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

            self._post_asset_modification()

    @rotation.setter
    def rotation(self, value):
        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [0.0, 0.0, 0.0, 1.0]
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
                value = rotation_from_euler_degrees(*value)
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 4:
                value = [float(v) for v in value]
            else:
                raise ValueError("Rotation should be of size 3 (Euler angles) or 4 (Quaternions")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_rotation = np.array(value) / np.linalg.norm(value)
        if not np.array_equal(self._rotation, new_rotation):
            self._rotation = new_rotation
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

            self._post_asset_modification()

    @scaling.setter
    def scaling(self, value):
        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [1.0, 1.0, 1.0]
            elif isinstance(value, (int, float)):
                value = [value, value, value]
            elif isinstance(value, (list, tuple, np.ndarray)) and len(value) == 3:
                value = [float(v) for v in value]
            elif not isinstance(value, np.ndarray):
                raise TypeError("Scale must be a float or a list of 3 numbers")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_scaling = np.array(value)
        if not np.array_equal(self._scaling, new_scaling):
            self._scaling = new_scaling
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)

            self._post_asset_modification()

    @transformation_matrix.setter
    def transformation_matrix(self, value):
        # Default to setting up from TRS if None
        if (value is None or isinstance(value, property)) and (
            self._position is not None and self._rotation is not None and self._scaling is not None
        ):
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
            return

        if self.dimensionality == 3:
            if value is None or isinstance(value, property):
                value = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            elif not isinstance(value, (list, tuple, np.ndarray)):
                raise TypeError("Transformation matrix must be a list of 4 lists of 4 numbers")
        elif self.dimensionality == 2:
            raise NotImplementedError()

        new_transformation_matrix = np.array(value)
        if not np.array_equal(self._transformation_matrix, new_transformation_matrix):
            self._transformation_matrix = new_transformation_matrix

            translation, rotation, scale = get_trs_from_transform_matrix(self._transformation_matrix)
            self._position = translation
            self._rotation = rotation
            self._scaling = scale

            self._post_asset_modification()

    def _post_asset_modification(self):
        if getattr(self.tree_root, "engine", None) is not None and self.tree_root.tree_root.engine.auto_update:
            self.tree_root.engine.update_asset(self)

    def _post_attach_parent(self, parent):
        """NodeMixing method call after attaching to a `parent`."""
        parent.tree_root._check_all_names_unique()  # Check that all names are unique in the tree
        if getattr(parent.tree_root, "engine", None) is not None:
            if parent.tree_root.engine.auto_update:
                parent.tree_root.engine.update_asset(self)

        # We have a couple of restrictions on parent/children nodes

        # Avoid circular imports (Reward functions are Asset) -
        # unfortunately we cannot do this test on the Reward function side
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
        """NodeMixing method call after detaching from a `parent`."""
        if getattr(parent.tree_root, "engine", None) is not None and parent.tree_root.engine.auto_update:
            parent.tree_root.engine.remove_asset(self)

    def _post_name_change(self, value):
        """NodeMixing method call after changing the name of a node."""
        self.tree_root._check_all_names_unique()  # Check that all names are unique in the tree

    def _check_all_names_unique(self):
        """Check that all names are unique in the tree."""
        seen = set()  # O(1) lookups
        for node in self.tree_descendants:
            if node.name not in seen:
                seen.add(node.name)
            else:
                raise ValueError("Node name '{}' is not unique".format(node.name))
