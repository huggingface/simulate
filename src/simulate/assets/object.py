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
""" A simulate Scene Object."""
import dataclasses
import itertools
from typing import Any, List, Optional, Tuple, Union

import numpy as np
import pyvista as pv

from simulate._vhacd import compute_vhacd

from ..utils import logging
from .articulation_body import ArticulationBodyComponent
from .asset import Asset
from .collider import Collider
from .material import Material
from .procgen.prims import generate_prims_maze
from .procgen.wfc import generate_2d_map, generate_map
from .rigid_body import RigidBodyComponent


logger = logging.get_logger(__name__)


def translate(
    surf,
    center: Union[Tuple[float, float, float], List[float], np.ndarray] = (0.0, 0.0, 0.0),
    new_direction: Union[Tuple[float, float, float], List[float], np.ndarray] = (1.0, 0.0, 0.0),
    original_direction: Union[Tuple[float, float, float], List[float], np.ndarray] = (1.0, 0.0, 0.0),
):
    """
    Translate and orient a mesh to a new center and direction.

    By default, the input mesh is considered centered at the origin
    and facing in the x direction.

    Adapted from pyvista's translate function.

    Args:
        surf (pyvista.PolyData):
            The mesh to translate.
        center (`Tuple` or `List[float]` or `np.ndarray`, *optional*, defaults to `(0.0, 0.0, 0.0)`):
            The new center of the mesh.
        new_direction (`Tuple` or `List[float]` or `np.ndarray`, *optional*, defaults to `(1.0, 0.0, 0.0)`):
            The new direction of the mesh.
        original_direction (`Tuple` or `List[float]` or `np.ndarray`, *optional*, defaults to `(1.0, 0.0, 0.0)`):
            The original direction of the mesh.
    """
    # Find rotation matrix that rotation original_direction to new_direction
    v = np.cross(original_direction, new_direction)
    s = np.linalg.norm(v)
    if s > 0:
        c = np.dot(original_direction, new_direction)
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        r = np.eye(3) + vx + vx.dot(vx) * ((1 - c) / (s**2))

        trans = np.zeros((4, 4))
        trans[:3, :3] = r
        trans[3, 3] = 1
        surf.transform(trans)

    if not np.allclose(center, [0.0, 0.0, 0.0]):
        surf.points += np.array(center)


class Object3D(Asset):
    """Create a 3D Object.

    Args:
        mesh (`pyvista.[UnstructuredGrid, MultiBlock, PolyData, DataSet]`, *optional*, defaults to None):
            The mesh of the object.
        material (`Material` or `List[Material]`, *optional*, defaults to None):
            The material of the object.
        name (`str`, *optional*, defaults to `None`):
            The name of the object.
        position (`List[float]`, *optional*, defaults to `[0.0, 0.0, 0.0]`):
            The position of the object.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the object is an actor.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the object is an actor.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the object has a rigid body.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the object has an articulation body.
        set_mesh_direction (`List[float]`, *optional*, defaults to `[1.0, 0.0, 0.0]`):
            The direction of the mesh.
        original_mesh_direction (`List[float]`, *optional*, defaults to `[1.0, 0.0, 0.0]`):
            The original direction of the mesh.
        recompute_normals (`bool`, *optional*, defaults to `True`):
            Whether to recompute normals per vertex for this object.
        parent (`Asset`, *optional*, defaults to `None`):
            The parent of the object.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            The children of the object.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        mesh: Optional[Union[pv.UnstructuredGrid, pv.MultiBlock, pv.PolyData, pv.DataSet]] = None,
        material: Optional[Union[Material, List[Material]]] = None,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        original_mesh_direction: Optional[List[float]] = None,
        recompute_normals: bool = True,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        super().__init__(name=name, position=position, is_actor=is_actor, parent=parent, children=children, **kwargs)

        if with_rigid_body and with_articulation_body:
            raise ValueError("Cannot have both rigid body and articulation body")
        if self.physics_component is None and with_rigid_body:
            self.physics_component = RigidBodyComponent()
        elif self.physics_component is None and with_articulation_body:
            self.physics_component = ArticulationBodyComponent()

        self.mesh = mesh if mesh is not None else pv.PolyData()

        if set_mesh_direction is not None:
            if original_mesh_direction is None:
                original_mesh_direction = [1.0, 0.0, 0.0]
            translate(mesh, (0, 0, 0), new_direction=set_mesh_direction, original_direction=original_mesh_direction)

        # Avoid having averaging normals at shared points
        # (pyvista behavior:https://docs.pyvista.org/api/core/_autosummary/pyvista.PolyData.compute_normals.html)
        if self.mesh is not None and recompute_normals:
            if isinstance(self.mesh, pv.MultiBlock):
                for i in range(self.mesh.n_blocks):
                    self.mesh[i].compute_normals(inplace=True, cell_normals=False, split_vertices=True)
            else:
                self.mesh.compute_normals(inplace=True, cell_normals=False, split_vertices=True)

        self.material = material if material is not None else Material()

        if isinstance(self.material, (list, tuple)) or isinstance(self.mesh, pv.MultiBlock):
            if not isinstance(self.mesh, pv.MultiBlock) or len(self.material) != self.mesh.n_blocks:
                raise ValueError("Number of materials must match number of blocks in mesh")

    def build_collider(
        self,
        max_convex_hulls=16,
        resolution=4000,
        minimum_volume_percent_error_allowed=1,
        max_recursion_depth=10,
        shrink_wrap=True,
        fill_mode="FLOOD_FILL",
        max_num_vertices_per_hull=64,
        async_ACD=True,
        min_edge_length=2,
        find_best_plane=False,
    ):
        """Build a collider from the mesh.

        Parameters
        ----------
        max_convex_hulls : int, optional
            Maximum number of convex hulls to generate, by default 16
        resolution : int, optional
            Resolution of the voxel grid, by default 4000
        minimum_volume_percent_error_allowed : float, optional
            Minimum volume percent error allowed, by default 1
        max_recursion_depth : int, optional
            Maximum recursion depth, by default 10
        shrink_wrap : bool, optional
            Shrink wrap, by default True
        fill_mode : str, optional
            Fill mode, by default "FLOOD_FILL"
        max_num_vertices_per_hull : int, optional
            Maximum number of vertices per hull, by default 64
        async_ACD : bool, optional
            Async ACD, by default True
        min_edge_length : int, optional
            Minimum edge length, by default 2
        find_best_plane : bool, optional
            Find best plane, by default False
        """
        if self.mesh is None:
            raise ValueError("Cannot build collider from empty mesh")

        kwargs = {
            "max_convex_hulls": max_convex_hulls,
            "resolution": resolution,
            "minimum_volume_percent_error_allowed": minimum_volume_percent_error_allowed,
            "max_recursion_depth": max_recursion_depth,
            "shrink_wrap": shrink_wrap,
            "fill_mode": fill_mode,
            "max_num_vertices_per_hull": max_num_vertices_per_hull,
            "async_ACD": async_ACD,
            "min_edge_length": min_edge_length,
            "find_best_plane": find_best_plane,
        }

        collider_hulls = []
        if isinstance(self.mesh, pv.MultiBlock):
            for i in range(self.mesh.n_blocks):
                collider_hulls.extend(compute_vhacd(self.mesh[i].points, self.mesh[i].faces, **kwargs))
        else:
            collider_hulls.extend(compute_vhacd(self.mesh.points, self.mesh.faces, **kwargs))

        if len(collider_hulls) == 1:
            mesh = pv.PolyData(collider_hulls[0][0], faces=collider_hulls[0][1])
            collider = Collider(type="mesh", mesh=mesh, convex=True)
        else:
            mesh = pv.MultiBlock()
            for hull in collider_hulls:
                mesh.append(pv.PolyData(hull[0], faces=hull[1]))
            collider = Collider(type="mesh", mesh=mesh, convex=True)

        children = self.tree_children
        self.tree_children = (children if children is not None else []) + (collider,)

        return self

    def copy(self, with_children: bool = True, **kwargs: Any) -> "Object3D":
        """
        Copy an Object3D node in a new (returned) object.

        By default, mesh and materials are copied in respectively new mesh and material.
        'share_material' and 'share_mesh' can be set to True to share mesh and/or material
        between original and copy instead of creating new one.

        Args:
            with_children (`bool`, *optional*, defaults to `True`):
                Whether to copy the children of the object.

        Returns:
            copy (`Object3D`):
                The copied object.
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

        physics_component_copy = None
        if self.physics_component is not None:
            physics_component_copy = dataclasses.replace(self.physics_component)

        copy_name = self.name + f"_copy{self._n_copies}"

        self._n_copies += 1
        instance_copy = type(self)(name=copy_name)
        instance_copy.mesh = mesh_copy
        instance_copy.material = material_copy
        instance_copy.position = self.position
        instance_copy.rotation = self.rotation
        instance_copy.scaling = self.scaling
        instance_copy.physics_component = physics_component_copy

        if with_children:
            copy_children = []
            for child in self.tree_children:
                copy_children.append(child.copy(**kwargs))
            instance_copy.tree_children = copy_children
            for child in instance_copy.tree_children:
                child._post_copy()

        return instance_copy

    def _post_name_change(self, value: Any):
        """NodeMixing method call after changing the name of a node."""
        for node in self.tree_children:
            if isinstance(node, Collider):
                node.name = self.name + "_collider"  # Let's keep the name of the collider in sync

    def _repr_info_str(self) -> str:
        """Used to add additional information to the __repr__ method."""
        if isinstance(self.mesh, pv.MultiBlock):
            mesh_str = f"Mesh(Multiblock, n_blocks={self.mesh.n_blocks}"
        else:
            mesh_str = f"Mesh(points={self.mesh.n_points}, cells={self.mesh.n_cells})"
        material_str = ""
        if hasattr(self, "material") and self.material is not None:
            base_color_str = ", ".join(f"{val:.1f}" for val in self.material.base_color)
            material_str = f", Material('{self.material.name}', base color=[{base_color_str}])"
        return f"{mesh_str}{material_str}"

    def plot(self, **kwargs):
        self.mesh.plot(**kwargs)


class Plane(Object3D):
    """
    Create a plane.

    Args:
        i_size (`float`, *optional*, defaults to `10.0`):
            Size of the plane in the i direction.
        j_size (`float`, *optional*, defaults to `10.0`):
            Size of the plane in the j direction.
        i_resolution (`int`, *optional*, defaults to `1`):
            Number of points on the plane in the i direction.
        j_resolution (`int`, *optional*, defaults to `1`):
            Number of points on the plane in the j direction.
        name (`str`, *optional*, defaults to `None`):
            Name of the plane.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the plane.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the plane is an actor or not.
        with_collider (`bool`, *optional*, defaults to `True`):
            Whether the plane has a collider or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the plane has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the plane has an articulation body or not.
        set_mesh_direction : list or tuple or np.ndarray, optional
            Direction the normal to the plane in `[x, y, z]`.
            Default to normal pointing in the `y` (up) direction.
        collider_thickness (`float`, *optional*, defaults to `None`):
            Thickness of the collider.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the plane.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the plane.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        i_size: float = 10.0,
        j_size: float = 10.0,
        i_resolution: int = 1,
        j_resolution: int = 1,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        is_actor: bool = False,
        with_collider: bool = True,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        collider_thickness: Optional[float] = None,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        original_mesh_direction = [0, -1, 0]
        mesh = pv.Plane(
            direction=original_mesh_direction,
            i_size=i_size,
            j_size=j_size,
            i_resolution=i_resolution,
            j_resolution=j_resolution,
        )

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            parent=parent,
            children=children,
            **kwargs,
        )

        if with_collider:
            collider_thickness = collider_thickness or min(i_size, j_size) / 100
            collider = Collider(
                name=self.name + "_collider",
                type="box",
                bounding_box=[i_size, collider_thickness, j_size],
                position=[0, -collider_thickness / 2, 0],
            )
            self.tree_children = (children if children is not None else []) + [collider]


class Sphere(Object3D):
    """
    Create a Sphere

    Args:
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the sphere.
        radius (`float`, *optional*, defaults to `1.0`):
            Sphere radius.
        theta_resolution (`int`, *optional*, defaults to `10`):
            Set the number of points in the longitude direction (ranging from `start_theta` to `end_theta`).
        phi_resolution (`int`, *optional*, defaults to `10`):
            Set the number of points in the latitude direction (ranging from `start_phi` to `end_phi`).
        start_theta (`float`, *optional*, defaults to `0.0`):
            Starting longitude angle.
        end_theta (`float`, *optional*, defaults to `360.0`):
            Ending longitude angle.
        start_phi (`float`, *optional*, defaults to `0.0`):
            Starting latitude angle.
        end_phi (`float`, *optional*, defaults to `180.0`):
            Ending latitude angle.
        sphere_type (`str`, *optional*, defaults to `"uv"`):
            One of 'uv' for a UV-sphere or 'ico' for an icosphere.
        with_collider (`bool`, *optional*, defaults to `True`):
            Set to true to automatically add an associated Sphere collider.
        name (`str`, *optional*, defaults to `None`):
            Name of the sphere.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the sphere is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the sphere has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the sphere has an articulation body or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the top of the sphere points to in ``[x, y, z]``.
            Default to top of sphere pointing in the ``y`` (up) direction.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the sphere.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the sphere.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        position: Optional[List[float]] = None,
        radius: float = 1.0,
        theta_resolution: int = 10,
        phi_resolution: int = 10,
        start_theta: float = 0.0,
        end_theta: float = 360.0,
        start_phi: float = 0.0,
        end_phi: float = 180.0,
        sphere_type: str = "uv",
        with_collider: bool = True,
        name: Optional[str] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if sphere_type not in ["uv", "ico"]:
            raise ValueError("Sphere type should be one of 'uv' or 'ico'.")

        from vtkmodules.vtkFiltersSources import vtkSphereSource

        sphere = vtkSphereSource()
        sphere.SetRadius(radius)
        sphere.SetThetaResolution(theta_resolution)
        sphere.SetPhiResolution(phi_resolution)
        sphere.SetStartTheta(start_theta)
        sphere.SetEndTheta(end_theta)
        sphere.SetStartPhi(start_phi)
        sphere.SetEndPhi(end_phi)
        sphere.SetLatLongTessellation(bool(sphere_type == "uv"))
        sphere.Update()
        mesh = pv.wrap(sphere.GetOutput())
        mesh.rotate_y(-90, inplace=True)

        super().__init__(
            name=name,
            mesh=mesh,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            recompute_normals=False,
            parent=parent,
            children=children,
            **kwargs,
        )

        if with_collider:
            collider = Collider(
                name=self.name + "_collider",
                type="sphere",
                bounding_box=[radius, radius, radius],
            )
            self.tree_children = (children if children is not None else []) + [collider]


# TODO: add rest of arguments
class Capsule(Object3D):
    """
    A capsule (a cylinder with hemispheric ends).

    Args:
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the capsule.
        height (`float`, *optional*, defaults to `1.0`):
            Height of the capsule.
        radius (`float`, *optional*, defaults to `0.2`):
            Radius of the capsule.
        theta_resolution (`int`, *optional*, defaults to `4`):
            Set the number of points in the longitude direction.
        phi_resolution (`int`, *optional*, defaults to `4`):
            Set the number of points in the latitude direction.
        sphere_type (`str`, *optional*, defaults to `"uv"`):
            One of 'uv' for a UV-sphere or 'ico' for an icosphere.
        with_collider (`bool`, *optional*, defaults to `True`):
            Set to true to automatically add an associated Sphere collider.
        name (`str`, *optional*, defaults to `None`):
            Name of the capsule.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the capsule is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the capsule has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the capsule has an articulation body or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the top of the capsule points to in ``[x, y, z]``.
            Default to top of capsule pointing in the ``y`` (up) direction.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the capsule.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the capsule.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        position: Optional[List[float]] = None,
        height: float = 1.0,
        radius: float = 0.2,
        theta_resolution: int = 4,
        phi_resolution: int = 4,
        sphere_type: str = "uv",
        with_collider: bool = True,
        name: Optional[str] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if sphere_type not in ["uv", "ico"]:
            raise ValueError("Sphere type should be one of 'uv' or 'ico'.")

        from vtkmodules.vtkFiltersSources import vtkCapsuleSource

        capsule = vtkCapsuleSource()  # TODO pyvista capsules are arranged on the side
        capsule.SetRadius(radius)
        capsule.SetCylinderLength(max(0.0, height - radius * 2))
        capsule.SetThetaResolution(theta_resolution)
        capsule.SetPhiResolution(phi_resolution)
        capsule.SetLatLongTessellation(bool(sphere_type == "uv"))
        capsule.Update()

        mesh = pv.wrap(capsule.GetOutput())

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )

        if with_collider:
            collider = Collider(
                name=self.name + "_collider",
                type="capsule",
                bounding_box=[radius, height, radius],
            )
            self.tree_children = (children if children is not None else []) + [collider]


class Cylinder(Object3D):
    """Create the surface of a cylinder.

    Args:
        height (`float`, *optional*, defaults to `1.0`):
            Height of the cylinder.
        radius (`float`, *optional*, defaults to `1.0`):
            Radius of the cylinder.
        resolution (`int`, *optional*, defaults to `16`):
            Number of points on the circular face of the cylinder.
        capping (`bool`, *optional*, defaults to `True`):
            Cap cylinder ends with polygons.
        name (`str`, *optional*, defaults to `None`):
            Name of the cylinder.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the cylinder.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the top of the cylinder points to in `[x, y, z]`.
            Default to top of cylinder pointing in the `y` (up) direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the cylinder is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the cylinder has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the cylinder has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the cylinder.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the cylinder.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        height: float = 1.0,
        radius: float = 1.0,
        resolution: int = 16,
        capping: bool = True,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        original_mesh_direction = [0, 1, 0]
        mesh = pv.Cylinder(
            direction=original_mesh_direction, radius=radius, height=height, resolution=resolution, capping=capping
        )

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Box(Object3D):
    """
    Create a box with solid faces for the given bounds.

    Args:
        bounds (`float` or `np.ndarray` or `List[float]`, *optional*, defaults to `(-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)`):
            Specify the bounding box of the cube as either:
             - a list of 6 floats:(xMin, xMax, yMin, yMax, zMin, zMax)
                => bounds are ``(xMin, xMax, yMin, yMax, zMin, zMax)``
            - a list of 3 floats: xSize, ySize, zSize
                => bounds are ``(-xSize/2, xSize/2, ySize/2, ySize/2, -zSize/2, zSize/2)``
            - a single float: size
                => bounds are ``(-size/2, size/2, size/2, size/2, -size/2, size/2)``
            If no value is provided, create a centered unit box
        level (`int`, *optional*, defaults to `0`):
            The level of subdivision of the box. The number of faces will be 6*4**level.
        quads (`bool`, *optional*, defaults to `True`):
            If `True`, the faces of the box will be quads. Otherwise, they will be triangles.
        with_colliders (`bool`, *optional*, defaults to `True`):
            Whether the box has colliders or not.
        name (`str`, *optional*, defaults to `None`):
            Name of the box.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the box.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the top of the box points to in `[x, y, z]`.
            Default to top of box pointing in the `y` (up) direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the box is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the box has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the box has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the box.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the box.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        bounds: Optional[Union[int, float, List[float], np.ndarray, Tuple[float, ...]]] = None,
        level: int = 0,
        quads: bool = True,
        with_collider: bool = True,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if bounds is None:
            bounds = (-0.5, 0.5, -0.5, 0.5, -0.5, 0.5)
        if isinstance(bounds, (float, int)):
            bounds = (-bounds / 2, bounds / 2, -bounds / 2, bounds / 2, -bounds / 2, bounds / 2)  # Make it a tuple
        if len(bounds) == 3:
            bounds = (
                -bounds[0] / 2,
                bounds[0] / 2,
                -bounds[1] / 2,
                bounds[1] / 2,
                -bounds[2] / 2,
                bounds[2] / 2,
            )  # Make it a tuple

        mesh = pv.Box(bounds=bounds, level=level, quads=quads)

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )

        if with_collider:
            bounding_box = [bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]]
            offset = [
                (bounds[0] + bounds[1]) / 2.0,
                (bounds[2] + bounds[3]) / 2.0,
                (bounds[4] + bounds[5]) / 2.0,
            ]
            collider = Collider(name=self.name + "_collider", type="box", bounding_box=bounding_box, offset=offset)
            self.tree_children = (children if children is not None else []) + [collider]


class Cone(Object3D):
    """
    Create a cone.

    Args:
        height (`float`, *optional*, defaults to `1.0`):
            Height of the cone.
        radius (`float`, *optional*, defaults to `1.0`):
            Radius of the cone.
        resolution (`int`, *optional*, defaults to `6`):
            Number of facets used to represent the cone.
        name (`str`, *optional*, defaults to `None`):
            Name of the cone.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the cone.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the top of the cone points to in `[x, y, z]`.
            Default to top of cone pointing in the `y` (up) direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the cone is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the cone has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the cone has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the cone.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the cone.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        height: float = 1.0,
        radius: float = 1.0,
        resolution: int = 6,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        original_mesh_direction = [0, 1, 0]
        mesh = pv.Cone(direction=original_mesh_direction, height=height, radius=radius, resolution=resolution)
        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Line(Object3D):
    """
    Create a line.

    Args:
        pointa (`np.ndarray` or `List[float]`, *optional*, defaults to `[-1.0, 0.0, 0.0]`):
            Location of the first point of the line.
        pointb (`np.ndarray` or `List[float]`, *optional*, defaults to `[1.0, 0.0, 0.0]`):
            Location of the second point of the line.
        resolution (`int`, *optional*, defaults to `1`):
            Number of pieces to divide line into.
        name (`str`, *optional*, defaults to `None`):
            Name of the line.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the line points to in `[x, y, z]`.
            Default to line pointing in the `x` direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the line is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the line has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the line has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the line.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the line.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        pointa: Optional[List[float]] = None,
        pointb: Optional[List[float]] = None,
        resolution: int = 1,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if pointa is None:
            pointa = [-1.0, 0.0, 0.0]
        if pointb is None:
            pointb = [1.0, 0.0, 0.0]
        mesh = pv.Line(pointa=pointa, pointb=pointb, resolution=resolution)

        super().__init__(
            mesh=mesh,
            name=name,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[1, 0, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class MultipleLines(Object3D):
    """Create multiple lines.

    Args:
        points (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            List of points defining a broken line, default is `[[-0.5, 0.0, 0.0], [0.5, 0.0, 0.0]]`.
        name (`str`, *optional*, defaults to `None`):
            Name of the multiple lines.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the multiple lines is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the multiple lines points to in `[x, y, z]`.
            Default to multiple lines pointing in the `x` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the multiple lines have a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the multiple lines have an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the multiple lines.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the multiple lines.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        points: Optional[List[List[float]]] = None,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if points is None:
            points = [[-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]
        mesh = pv.MultipleLines(points=points)

        super().__init__(
            mesh=mesh,
            name=name,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[1, 0, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Tube(Object3D):
    """Create a tube that goes from point A to point B.

    Args:
        pointa (`np.ndarray` or `List[float]`, *optional*, defaults to `[-1.0, 0.0, 0.0]`):
            Location of the first point of the tube.
        pointb (`np.ndarray` or `List[float]`, *optional*, defaults to `[1.0, 0.0, 0.0]`):
            Location of the second point of the tube.
        resolution (`int`, *optional*, defaults to `1`):
            Number of pieces to divide tube into.
        radius (`float`, *optional*, defaults to `0.1`):
            Minimum tube radius (minimum because the tube radius may vary).
        n_sides (`int`, *optional*, defaults to `16`):
            Number of sides of the tube.
        name (`str`, *optional*, defaults to `None`):
            Name of the tube.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the tube is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the tube points to in `[x, y, z]`.
            Default to tube pointing in the `y` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the tube has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the tube has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the tube.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the tube.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        pointa: Optional[List[float]] = None,
        pointb: Optional[List[float]] = None,
        resolution: int = 1,
        radius: float = 1.0,
        n_sides: int = 16,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if pointa is None:
            pointa = [-1.0, 0.0, 0.0]
        if pointb is None:
            pointb = [1.0, 0.0, 0.0]
        mesh = pv.Tube(pointa=pointa, pointb=pointb, radius=radius, resolution=resolution, n_sides=n_sides)

        super().__init__(
            mesh=mesh,
            name=name,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Polygon(Object3D):
    """
    Create a polygon.

    Args:
        points (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            List of points defining the polygon,
            e.g. `[[0, 0, 0], [1, 0, -.1], [.8, 0, .5], [1, 0, 1], [.6, 0, 1.2], [0, 0, .8]]`.
            The polygon is defined by an ordered list of three or more points lying in a plane.
            The polygon normal is implicitly defined by a counterclockwise ordering of
            its points using the right-hand rule.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the polygon.
        name (`str`, *optional*, defaults to `None`):
            Name of the polygon.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the polygon is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the polygon points to in `[x, y, z]`.
            Default to polygon pointing in the `y` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the polygon has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the polygon has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the polygon.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the polygon.
        with_colliders (`bool`, *optional*, defaults to `False`):
            Whether the polygon has colliders or not.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        points: List[List[float]],
        position: Optional[List[float]] = None,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        with_collider: bool = False,
        **kwargs: Any,
    ):
        from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkPolygon

        # Setup points
        num_pts = len(points)
        v_points = pv.vtk_points(points)

        # Create the polygon
        polygon = vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(num_pts)
        for i in range(num_pts):
            polygon.GetPointIds().SetId(i, i)

        # Add the polygon to a list of polygons
        polygons = vtkCellArray()
        polygons.InsertNextCell(polygon)

        # Create a PolyData
        polygon_poly_data = vtkPolyData()
        polygon_poly_data.SetPoints(v_points)
        polygon_poly_data.SetPolys(polygons)

        mesh = pv.PolyData(polygon_poly_data)

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )

        if with_collider:
            collider = Collider(
                name=self.name + "_collider",
                type="mesh",
                mesh=mesh,
            )
            self.tree_children = (children if children is not None else []) + [collider]


class RegularPolygon(Object3D):
    """
    Create a regular polygon.

    Args:
        radius (`float`, *optional*, defaults to `1.0`):
            Radius of the regular polygon.
        n_sides (`int`, *optional*, defaults to `6`):
            Number of sides of the regular polygon.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the regular polygon.
        name (`str`, *optional*, defaults to `None`):
            Name of the regular polygon.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the regular polygon is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the regular polygon points to in `[x, y, z]`.
            Default to regular polygon pointing in the `y` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the regular polygon has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the regular polygon has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the regular polygon.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the regular polygon.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        radius: float = 1.0,
        n_sides: int = 6,
        position: Optional[List[float]] = None,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        original_mesh_direction = [0, 1, 0]
        mesh = pv.Polygon(radius=radius, normal=original_mesh_direction, n_sides=n_sides)

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Ring(Object3D):
    """Create a polygonal disk with a hole in the center.

    The disk has zero height. The user can specify the inner and outer
    radius of the disk, and the radial and circumferential resolution
    of the polygonal representation.

    Args:
        inner (`float`, *optional*, defaults to `0.25`):
            Inner radius of the ring.
        outer (`float`, *optional*, defaults to `0.5`):
            Outer radius of the ring.
        r_res (`int`, *optional*, defaults to `1`):
            Number of points in radial direction.
        c_res (`int`, *optional*, defaults to `6`):
            Number of points in circumferential direction.
        name (`str`, *optional*, defaults to `None`):
            Name of the ring.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the ring.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the ring points to in `[x, y, z]`.
            Default to ring pointing in the `y` direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the ring is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the ring has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the ring has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the ring.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the ring.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    # TODO(thomas) add back center and normal and see how to handle that for 2D/3D stuff
    def __init__(
        self,
        inner: float = 0.25,
        outer: float = 0.5,
        r_res: int = 1,
        c_res: int = 6,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        original_mesh_direction = [0, 1, 0]
        mesh = pv.Disc(inner=inner, outer=outer, normal=original_mesh_direction, r_res=r_res, c_res=c_res)

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Text3D(Object3D):
    """
    Create 3D text from a string.

    Args:
        string (`str`, *optional*, defaults to `None`):
            String to be converted to 3D text.
        depth (`float`, *optional*, defaults to `0.5`):
            Depth of the text.
        name (`str`, *optional*, defaults to `None`):
            Name of the text.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the text.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the text points to in `[x, y, z]`.
            Default to text pointing in the `z` direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the text is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the text has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the text has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the text.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the text.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        string: str = "Hello",
        depth: float = 0.5,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        mesh = pv.Text3D(string=string, depth=depth)
        mesh.rotate_y(-90, inplace=True)
        original_mesh_direction = [0, 0, -1]
        translate(mesh, (0, 0, 0), new_direction=original_mesh_direction)

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Triangle(Object3D):
    """Create a triangle defined by 3 points.

    Args:
        points (`np.ndarray` or `List[List[float]]`, *optional*, defaults to `None`):
            Points of the triangle.
        name (`str`, *optional*, defaults to `None`):
            Name of the triangle.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the triangle is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the triangle points to in `[x, y, z]`.
            Default to triangle pointing in the `y` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the triangle has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the triangle has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the triangle.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the triangle.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        points: Optional[List[List[float]]] = None,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        mesh = pv.Triangle(points=points)

        super().__init__(
            mesh=mesh,
            name=name,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Rectangle(Object3D):
    """Create a rectangle defined by 4 points.

    Args:
        points (`np.ndarray` or `List[List[float]]`, *optional*, defaults to `None`):
            Points of the rectangle.
        name (`str`, *optional*, defaults to `None`):
            Name of the rectangle.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the rectangle is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the rectangle points to in `[x, y, z]`.
            Default to rectangle pointing in the `y` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the rectangle has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the rectangle has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the rectangle.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the rectangle.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        points: Optional[List[List[float]]] = None,
        name: Optional[str] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        mesh = pv.Rectangle(points=points)

        super().__init__(
            mesh=mesh,
            name=name,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=[0, 1, 0],
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class Circle(Object3D):
    """Create a single PolyData circle defined by radius in the XY plane.

    Args:
        radius (`float`, *optional*, defaults to `0.5`):
            Radius of the circle.
        resolution (`int`, *optional*, defaults to `100`):
            Number of points to define the circle.
        name (`str`, *optional*, defaults to `None`):
            Name of the circle.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the circle.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the circle is an actor or not.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the circle points to in `[x, y, z]`.
            Default to circle pointing in the `y` direction.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the circle has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the circle has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the circle.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the circle.
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        radius: float = 0.5,
        resolution: int = 100,
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        is_actor: bool = False,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        mesh = pv.Circle(radius=radius, resolution=resolution)
        mesh.rotate_y(-90, inplace=True)
        original_mesh_direction = [0, 1, 0]
        translate(mesh, (0, 0, 0), new_direction=original_mesh_direction)

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class StructuredGrid(Object3D):
    """
    Create a 3D grid (structured plane) defined by lists of X, Y and Z positions of points.

    Args:
        x (`np.ndarray` or `List[List[float]]`):
            Position of the points in x direction.
        y (`np.ndarray` or `List[List[float]]`):
            Position of the points in y direction.
        z (`np.ndarray` or `List[List[float]]`):
            Position of the points in z direction.
        name (`str`, *optional*, defaults to `None`):
            Name of the structured grid.
        position (`np.ndarray` or `List[float]`, *optional*, defaults to `[0, 0, 0]`):
            Position of the structured grid.
        set_mesh_direction (`np.ndarray` or `List[float]`, *optional*, defaults to `None`):
            Direction the structured grid points to in `[x, y, z]`.
            Default to structured grid pointing in the `y` direction.
        is_actor (`bool`, *optional*, defaults to `False`):
            Whether the structured grid is an actor or not.
        with_rigid_body (`bool`, *optional*, defaults to `False`):
            Whether the structured grid has a rigid body or not.
        with_articulation_body (`bool`, *optional*, defaults to `False`):
            Whether the structured grid has an articulation body or not.
        parent (`Asset`, *optional*, defaults to `None`):
            Parent of the structured grid.
        children (`Asset` or `List[Asset]`, *optional*, defaults to `None`):
            Children of the structured grid.

    Examples:

    ```python
    # create a 5x5 mesh grid
    xrng = np.arange(-2, 3, dtype=np.float32)
    zrng = np.arange(-2, 3, dtype=np.float32)
    x, z = np.meshgrid(xrng, zrng)
    # let's make the y-axis a sort of cone
    y = 1. / np.sqrt(x*x + z*z + 0.1)
    asset = sm.StructuredGrid(x, y, z)
    ```
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        x: Union[np.ndarray, List[List[float]]],
        y: Union[np.ndarray, List[List[float]]],
        z: Union[np.ndarray, List[List[float]]],
        name: Optional[str] = None,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)
        if not isinstance(z, np.ndarray):
            z = np.array(z)

        # If it is a structured grid, extract the surface mesh (PolyData)
        mesh = pv.StructuredGrid(x, y, z).extract_surface()
        original_mesh_direction = [0, 1, 0]
        translate(mesh, (0, 0, 0), new_direction=original_mesh_direction, original_direction=(0, 1, 0))

        super().__init__(
            mesh=mesh,
            name=name,
            position=position,
            is_actor=is_actor,
            set_mesh_direction=set_mesh_direction,
            original_mesh_direction=original_mesh_direction,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class ProcgenGrid(Object3D):
    """Create a procedural generated 3D grid (structured plane) from
        tiles / previous map.
    Parameters
    ----------
    sample_map : np.ndarray or python list of lists of floats
        Map to procedurally generate from.
    specific_map: np.ndarray or python list of lists of floats
        Map to show as it is.
    tiles : list of tiles
        Tiles for procedural generation when using generation from tiles and neighbors definitions.
        Tiles must be NxN np.ndarray that define height maps. In the future, we plan to support
        more generic tiles.
    neighbors: list of available neighbors for each tile
        Expects pair of tiles.
    symmetries: list of char
        Expects a list of symmetry definitions. If passed, you must define a symmetry for each tile.
        Possible symmetries are "X", "I" / "/", "T" / "L", another character, and each character defines
        the tile with the same level of symmetry as the character:
        - X: has symmetry in all ways. So it has 1 different format.
        - I / `/`: when rotated, it's different from the original tile. Has 2 different formats.
        - T / L: Has 4 different formats.
        - other characters: the algorithm supposes it has 8 different formats.
    weights: list of floats
        sampling weights for each of the tiles
    width: int
        width of the generated map
    height: int
        height of the generated map
    shallow: bool
        Indicates whether procedural generation mesh should be generated in simenv or not.
        When it's true, we just return the map returned by the algorithm without
        actually creating the mesh in simenv.
        Created for the purpose of optimizing certain environments such as XLand.
    seed: int
        Random seed used for procedural generation.
    algorithm_args: dict
        Extra arguments to be passed to the procedural generation.
    Returns
    -------
    Examples
    --------
    """

    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        sample_map: Union[np.ndarray, List[List[List[int]]]] = None,
        specific_map: Union[np.ndarray, List[List[List[int]]]] = None,
        tiles: Optional[List] = None,
        neighbors: Optional[List] = None,
        symmetries: Optional[List] = None,
        weights: Optional[List] = None,
        width: int = 9,
        height: int = 9,
        shallow: bool = False,
        algorithm_args: Optional[dict] = None,
        seed: int = None,
        name: Optional[str] = None,
        is_actor: bool = False,
        position: Optional[List[float]] = None,
        set_mesh_direction: Optional[List[float]] = None,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        verbose: bool = False,
        **kwargs: Any,
    ):

        if seed is None:
            seed = np.random.randint(0, 100000)
            if verbose:
                logger.info("Seed:", seed)

        # Seeding
        np.random.seed(seed)

        if sample_map is not None and not isinstance(sample_map, np.ndarray):
            sample_map = np.array(sample_map)

        if specific_map is not None and not isinstance(specific_map, np.ndarray):
            specific_map = np.array(specific_map)

        if algorithm_args is None:
            algorithm_args = {}

        # Handle when user doesn't pass arguments properly
        if (tiles is None or neighbors is None) and sample_map is None and specific_map is None:
            raise ValueError("Insert tiles / neighbors or a map to sample from.")

        # Get coordinates and image from procedural generation
        all_args = {
            "width": width,
            "height": height,
            "sample_map": sample_map,
            "tiles": tiles,
            "neighbors": neighbors,
            "weights": weights,
            "symmetries": symmetries,
            **algorithm_args,
        }

        if shallow:
            if specific_map is None:
                map_2ds = generate_2d_map(**all_args)
                # We take the first map (if nb_samples > 1), since this object has
                # support for a single map for now
                self.map_2d = map_2ds[0]

            else:
                self.map_2d = specific_map

        else:
            # Saves these for other functions that might use them
            # We take index 0 since generate_map is now vectorized, but we don't have
            # support for multiple maps on this object yet.
            coordinates, map_2ds = generate_map(specific_map=specific_map, **all_args)
            self.coordinates, self.map_2d = coordinates[0], map_2ds[0]

            # If it is a structured grid, extract the surface mesh (PolyData)
            mesh = pv.StructuredGrid(*self.coordinates).extract_surface()
            original_mesh_direction = [0, 1, 0]

            super().__init__(
                mesh=mesh,
                name=name,
                position=position,
                is_actor=is_actor,
                set_mesh_direction=set_mesh_direction,
                original_mesh_direction=original_mesh_direction,
                with_rigid_body=with_rigid_body,
                with_articulation_body=with_articulation_body,
                parent=parent,
                children=children,
                **kwargs,
            )

    def generate_3D(
        self,
        name: Optional[str] = None,
        is_actor: bool = False,
        with_rigid_body: bool = False,
        with_articulation_body: bool = False,
        parent: Optional["Asset"] = None,
        children: Optional[Union["Asset", List["Asset"]]] = None,
        **kwargs: Any,
    ):
        """
        Function for creating the mesh in case the creation of map was shallow.
        """
        coordinates, _ = generate_map(specific_map=self.map_2d)
        self.coordinates = coordinates[0]

        # If it is a structured grid, extract the surface mesh (PolyData)
        mesh = pv.StructuredGrid(*self.coordinates).extract_surface()
        super().__init__(
            mesh=mesh,
            name=name,
            is_actor=is_actor,
            with_rigid_body=with_rigid_body,
            with_articulation_body=with_articulation_body,
            parent=parent,
            children=children,
            **kwargs,
        )


class ProcGenPrimsMaze3D(Asset):
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        width: int,
        depth: int,
        name: Optional[str] = None,
        wall_keep_prob: float = 0.5,
        wall_material: Optional[Material] = None,
        **kwargs: Any,
    ):
        self.width = width
        self.depth = depth
        self.wall_keep_prob = wall_keep_prob * 10
        if wall_material is None:
            wall_material = Material(base_color=[0.8, 0.8, 0.8])
        self.wall_material = wall_material
        if name is not None:
            self.name = name
        super().__init__(**kwargs)
        self._generate()

    def _generate(self):
        """Generate the maze."""
        walls = generate_prims_maze((self.width, self.depth), keep_prob=int(self.wall_keep_prob))

        for i, wall in enumerate(walls):
            px = (wall[0] + wall[2]) / 2
            pz = (wall[1] + wall[3]) / 2
            sx = abs(wall[2] - wall[0]) + 0.1
            sz = abs(wall[3] - wall[1]) + 0.1

            self += Box(
                name=f"{self.name}_wall_{i}",
                position=[px, 0.5, pz],
                material=self.wall_material,
                scaling=[sx, 1.0, sz],
                with_collider=True,
            )
