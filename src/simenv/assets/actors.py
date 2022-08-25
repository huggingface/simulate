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

from .camera import Camera
from .collider import Collider
from .controller import ActionMapping, Controller
from .object import Capsule
from .rigid_body import RigidBodyComponent


class SimpleActor(Capsule):
    """Create a Simple RL Actor in the Scene

        A simple actor is a capsule asset with:
        - a Camera as a child asset for observation device
        - a RigidBodyComponent component with a mass of 1.0
        - a discrete controller

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
        collider: Optional[Collider] = None,
        camera_height: Optional[int] = None,
        camera_width: Optional[int] = None,
        transformation_matrix=None,
        parent=None,
        children=None,
    ):

        if position is None:
            position = [0, 0.51, 0]  # A bit above the reference plane

        camera_name = None
        if name is not None:
            camera_name = f"{name}_camera"
        if camera_height is None:
            camera_height = 32
        if camera_width is None:
            camera_width = 40
        self.camera = Camera(name=camera_name, width=camera_width, height=camera_height, position=[0, 0.75, 0])
        children = children + self.camera if children is not None else self.camera

        super().__init__(
            name=name,
            position=position,
            rotation=rotation,
            scaling=scaling,
            parent=parent,
            children=children,
            collider=collider,
            transformation_matrix=transformation_matrix,
        )

        # Rescale the actor
        if scaling is not None:
            self.scale(scaling)

        # Move our actor a bit higher than the ground
        self.translate_y(0.51)

        # Add our physics component (by default the actor can only rotation along y axis)
        self.physics_component = RigidBodyComponent(mass=mass, constraints=["freeze_rotation_x", "freeze_rotation_z"])

        # Create our action maps to physics engine effects
        mapping = [
            ActionMapping("change_relative_rotation", axis=[0, 1, 0], amplitude=-90),
            ActionMapping("change_relative_rotation", axis=[0, 1, 0], amplitude=90),
            ActionMapping("change_relative_position", axis=[1, 0, 0], amplitude=2.0),
        ]
        self.controller = Controller(n=3, mapping=mapping)

    def copy(self, with_children=True, **kwargs) -> "SimpleActor":
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

        instance_copy.physics_component = self.physics_component

        return instance_copy
