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
""" Some pre-built simple agents."""
import itertools
from typing import List, Optional, Union

from .actuator import ActionMapping, Actuator
from .camera import Camera
from .object import Capsule, Sphere
from .rigid_body import RigidBodyComponent


class SimpleActor(Sphere):
    """Creates a bare-bones RL agent in the scene.

    A SimpleActor is a sphere asset with:
    - basic XYZ positional control (continuous),
    - mass of 1 (default)
    - no attached Camera

    """

    dimensionality = 3
    __NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self,
        name=None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        transformation_matrix=None,
        parent=None,
        children=None,
    ):

        if position is None:
            position = [0, 0, 0]  # at origin

        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            transformation_matrix=transformation_matrix,
            is_actor=True,
            with_collider=True,
        )

        # Rescale the actor
        if scaling is not None:
            self.scale(scaling)

        # Add our physics component =
        self.physics_component = RigidBodyComponent()

        # Create our action maps to physics engine effects
        mapping = [
            ActionMapping("change_position", axis=[1, 0, 0]),
            ActionMapping("change_position", axis=[0, 1, 0]),
            ActionMapping("change_position", axis=[0, 0, 1]),
        ]
        self.actuator = Actuator(n=3, mapping=mapping)

    def copy(self, with_children=True, **kwargs) -> "SimpleActor":
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

        instance_copy.physics_component = self.physics_component

        return instance_copy


class EgocentricCameraActor(Capsule):
    """Create an Egocentric RL Actor in the Scene -- essentially a basic first-person agent.

        An egocentric actor is a capsule asset with:
        - a Camera as a child asset for observation device
        - a RigidBodyComponent component with a mass of 1.0
        - a discrete actuator

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
        mass: Optional[float] = 1.0,
        name=None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scaling: Optional[Union[float, List[float]]] = None,
        camera_height: Optional[int] = 40,
        camera_width: Optional[int] = 40,
        transformation_matrix=None,
        parent=None,
        children=None,
    ):

        if position is None:
            position = [0, 1.05, 0]  # A bit above the reference plane

        camera_name = None
        if name is not None:
            camera_name = f"{name}_camera"
        self.camera = Camera(name=camera_name, width=camera_width, height=camera_height, position=[0, 0.25, 0])
        children = children + self.camera if children is not None else self.camera

        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            transformation_matrix=transformation_matrix,
            is_actor=True,
            with_collider=True,
        )

        # Rescale the actor
        if scaling is not None:
            self.scale(scaling)

        # Add our physics component (by default the actor can only rotation along y axis)
        self.physics_component = RigidBodyComponent(
            mass=mass, constraints=["freeze_rotation_x", "freeze_rotation_z", "freeze_position_y"]
        )

        # Create our action maps to physics engine effects
        mapping = [
            ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=-10),
            ActionMapping("change_rotation", axis=[0, 1, 0], amplitude=10),
            ActionMapping("change_position", axis=[1, 0, 0], amplitude=0.1),
        ]
        self.actuator = Actuator(n=3, mapping=mapping)

    def copy(self, with_children=True, **kwargs) -> "EgocentricCameraActor":
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

        instance_copy.physics_component = self.physics_component

        return instance_copy
