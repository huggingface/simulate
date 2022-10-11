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
""" A simulate Collider."""
import dataclasses
import itertools
from dataclasses import InitVar, dataclass, fields
from typing import Any, ClassVar, List, Optional, Tuple, Union

import numpy as np
import pyvista as pv

from .asset import Asset, get_transform_from_trs, get_trs_from_transform_matrix, rotation_from_euler_degrees
from .gltf_extension import GltfExtensionMixin
from .physic_material import PhysicMaterial


ALLOWED_COLLIDER_TYPES = ["box", "sphere", "capsule", "mesh"]


@dataclass(repr=False)
class Collider(Asset, GltfExtensionMixin, gltf_extension_name="HF_colliders", object_type="node"):
    """
    A physics collider.

    Args:
        type (`str`, *optional*, defaults to `box`):
            The type of shape of the collider. Can be one of:
            [
                `box`,
                `sphere`,
                `capsule`,
                `mesh`,
            ]
        bounding_box (`List[float]`, *optional*, defaults to `None`):
            The XYZ size of the bounding box that encapsulates the collider.
            The collider will attempt to fill the bounding box.
        offset (`List[float]`, *optional*, defaults to `[0, 0, 0]`):
            The position offset of the collider relative to the object it's attached to.
        intangible (`bool`, *optional*, defaults to `False`):
            Whether the collider should act as an intangible trigger.
        convex (`bool`, *optional*, defaults to `False`):
            Whether the collider is convex when using the mesh collider type --
            convex mesh Colliders collide with other mesh Colliders.
        physic_material (`int`, *optional*, defaults to `None`):
            The index of the physic material to use for the collider.

        name (`str`, *optional*, defaults to `None`):
            The name of the collider.
        mesh (`pyvista.UnstructuredGrid` or `pyvista.PolyData` or `pyvista.MultiBlock`, *optional*, defaults to `None`):
            The mesh of the collider.
        material (`Material`, *optional*, defaults to `None`):
            The material of the collider.
        position (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The position of the collider.
        rotation (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The rotation of the collider in Euler angles (in degrees).
        scaling (`float` or `List[float]`, *optional*, defaults to `1.0`):
            The scaling of the collider.
        transformation_matrix (`List[float]`, *optional*, defaults to `None`):
            The transformation matrix of the collider.
        parent (`Node`, *optional*, defaults to `None`):
            The parent of the collider.
        children (`List[Node]`, *optional*, defaults to `None`):
            The children of the collider.
        created_from_file (`str`, *optional*, defaults to `None`):
            The path to the file from which the collider was created.
    """

    type: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    offset: Optional[List[float]] = None
    intangible: Optional[bool] = None
    convex: Optional[bool] = None
    physic_material: Optional[int] = None

    name: InitVar[Optional[str]] = None
    mesh: InitVar[Optional[Union[pv.UnstructuredGrid, pv.PolyData, pv.MultiBlock]]] = None
    material: InitVar[Optional[Any]] = None
    position: InitVar[Optional[Union[List[float], np.ndarray]]] = None
    rotation: InitVar[Optional[Union[List[float], np.ndarray]]] = None
    scaling: InitVar[Optional[Union[float, List[float], np.ndarray]]] = None
    transformation_matrix: InitVar[Optional[List[float]]] = None
    parent: InitVar[Optional["Asset"]] = None
    children: InitVar[Optional[List["Asset"]]] = None
    created_from_file: InitVar[Optional[str]] = None

    __NEW_ID: ClassVar[Any] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __post_init__(
        self,
        name: Optional[str] = None,
        mesh: Optional[Union[pv.UnstructuredGrid, pv.PolyData, pv.MultiBlock]] = None,
        material: Optional[Any] = None,
        position: Optional[Union[List[float], np.ndarray]] = None,
        rotation: Optional[Union[List[float], np.ndarray]] = None,
        scaling: Optional[Union[float, List[float], np.ndarray]] = None,
        transformation_matrix: Optional[List[float]] = None,
        parent: Optional["Asset"] = None,
        children: Optional[List["Asset"]] = None,
        created_from_file: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            transformation_matrix=transformation_matrix,
            parent=parent,
            children=children,
            created_from_file=created_from_file,
        )

        # Handle mesh and material
        self.mesh = mesh
        # Avoid having averaging normals at shared points
        # (pyvista behavior:https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyData.compute_normals.html)
        if self.mesh is not None:
            if isinstance(self.mesh, pv.MultiBlock):
                for i in range(self.mesh.n_blocks):
                    self.mesh[i].compute_normals(inplace=True, cell_normals=False, split_vertices=True)
            else:
                self.mesh.compute_normals(inplace=True, cell_normals=False, split_vertices=True)
        self.material = material
        if self.material is not None and not isinstance(material, PhysicMaterial):
            raise TypeError(f"The material given to a Collider must be a PhysicsMaterial and not a {type(material)}")

        if self.type is None:
            if self.mesh is not None:
                self.type = "mesh"
            else:
                self.type = "box"

        if self.type not in ALLOWED_COLLIDER_TYPES:
            raise ValueError(f"Collider type {self.type} is not supported.")

        # if self.bounding_box is None and self.mesh is None:
        #     raise ValueError(
        #         "You should provide either a bounding box (for box, sphere and capsule colliders) or a mesh"
        #     )

        if self.bounding_box is not None and len(self.bounding_box) != 3:
            raise ValueError("Collider bounding_box must be a list of 3 numbers")

    def copy(self, with_children: bool = True, **kwargs: Any) -> "Collider":
        """
        Copy an Object3D node in a new (returned) object.

        By default, mesh and materials are copied in respectively new mesh and material.
        'share_material' and 'share_mesh' can be set to True to share mesh and/or material
        between original and copy instead of creating new one.

        Args:
            with_children (`bool`, *optional*, defaults to `True`):
                Whether to copy the children of the node.

        Returns:
            copy (`Collider`):
                The copy of the collider.
        """
        share_material = kwargs.get("share_material", False)
        share_mesh = kwargs.get("share_mesh", False)

        mesh_copy = None
        if self.mesh is not None:
            if share_mesh:
                mesh_copy = self.mesh
            else:
                mesh_copy = self.mesh.copy()

        material_copy = None
        if self.material is not None:
            if share_material:
                material_copy = self.material
            else:
                material_copy = self.material.copy()

        copy_name = self.name + f"_copy{self._n_copies}"

        self._n_copies += 1

        instance_copy = dataclasses.replace(self)
        instance_copy.mesh = mesh_copy
        instance_copy.material = material_copy
        instance_copy.name = copy_name

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children
            for child in instance_copy.tree_children:
                child._post_copy()
        else:
            instance_copy.tree_children = []

        return instance_copy

    def __repr__(self) -> str:
        fields_str = ", ".join([f"{f.name}={getattr(self, f.name)}" for f in fields(self)])
        mesh_str = ""
        if getattr(self, "mesh", None) is not None:
            if isinstance(self.mesh, pv.MultiBlock):
                mesh_str = f"Mesh(Multiblock, n_blocks={self.mesh.n_blocks}"
            else:
                mesh_str = f"Mesh(points={self.mesh.n_points}, cells={self.mesh.n_cells})"
        material_str = ""
        if getattr(self, "material", None) is not None:
            material_str = str(self.material)
        return f"{self.name}: {self.__class__.__name__}({fields_str}, {mesh_str}, {material_str})"

    def plot(self, **kwargs):
        if self.mesh is not None:
            self.mesh.plot(**kwargs)

    ##############################
    # Properties copied from Asset()
    # We need to redefine them here otherwise the dataclass lose them since
    # they are also in the __init__ signature
    #
    # Need to be updated if Asset() is updated
    ##############################
    @property
    def position(self) -> np.ndarray:
        """
        Get the position of the collider in the scene.

        Returns:
            position (`List[float]` or `np.ndarray`):
                The position of the collider in the scene.
        """
        return self._position

    @property
    def rotation(self) -> np.ndarray:
        """
        Get the rotation of the collider in the scene.

        Returns:
            rotation (`List[float]` or `np.ndarray`):
                The rotation of the collider in the scene.
        """
        return self._rotation

    @property
    def scaling(self) -> np.ndarray:
        """
        Get the scaling of the collider in the scene.

        Returns:
            scaling (`List[float]` or `np.ndarray`):
                The scaling of the collider in the scene.
        """
        return self._scaling

    @property
    def transformation_matrix(self) -> np.ndarray:
        """
        Get the transformation matrix of the collider in the scene.

        Returns:
            transformation_matrix (`np.ndarray`):
                The transformation matrix of the collider in the scene.
        """
        if self._transformation_matrix is None:
            self._transformation_matrix = get_transform_from_trs(self._position, self._rotation, self._scaling)
        return self._transformation_matrix

    # setters for position/rotation/scale
    @position.setter
    def position(self, value: Optional[Union[property, List, Tuple, np.ndarray]]):
        """
        Set the position of the collider in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The position of the collider in the scene.
        """
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
    def rotation(self, value: Optional[Union[property, List, Tuple, np.ndarray]]):
        """
        Set the rotation of the collider in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The rotation of the collider in the scene.
        """
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
    def scaling(self, value: Optional[Union[property, List, Tuple, np.ndarray]]):
        """
        Set the scaling of the collider in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The scaling of the collider in the scene.
        """
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
    def transformation_matrix(self, value: Optional[Union[property, List, Tuple, np.ndarray]]):
        """
        Set the transformation matrix of the collider in the scene.

        Args:
            value (`float` or `List[float]` or `np.ndarray` or `Tuple` or `property`, *optional*, defaults to `None`):
                The transformation matrix of the collider in the scene.
        """
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
