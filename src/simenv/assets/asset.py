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
import math
import uuid
import itertools
from typing import Optional, Union, Sequence

import numpy as np

from .anytree import NodeMixin
from .utils import camelcase_to_snakecase


class Asset(NodeMixin, object):
    dimensionality = 3  # 2 for bi-dimensional assets and 3 for tri-dimensional assets (default is 3)
    NEW_ID = itertools.count()  # Singleton to count instances of the classes for automatic naming

    def __init__(
        self, name: Optional[str] = None, translation=None, rotation=None, scale=None, parent=None, children=None
    ):
        self.id = next(self.__class__.NEW_ID)
        if name is not None:
            name = camelcase_to_snakecase(self.__class__.__name__ + f"_{self.id:3}")
        self.name = name

        self.parent = parent
        if children:
            self.children = children

        self.translation = translation
        self.rotation = rotation
        self.scale = scale

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Name should be a string.")
        if self.parent is not None:
            self.parent
        self._name = value

    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0]
            elif len(value) != 3:
                raise ValueError("Translation should be of size 3 (X, Y, Z)")
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._translation = tuple(value)

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [0.0, 0.0, 0.0, 0.0]
            elif len(value) == 3:
                value = quat_from_euler(*value)
            elif len(value) != 4:
                raise ValueError("Rotation should be of size 3 (Euler angles) or 4 (Quaternions")
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._rotation = tuple(value)

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        if self.dimensionality == 3:
            if value is None:
                value = [1.0, 1.0, 1.0]
            elif len(value) == 1:
                value = [value, value, value]
            elif len(value) != 3:
                raise ValueError("Scale should be of size 1 (Uniform scale) or 3 (X, Y, Z)")
        elif self.dimensionality == 2:
            raise NotImplementedError()
        self._scale = tuple(value)

    def _post_detach_children(self, children):
        """ After detaching `children`. We remove the attributes associated to the children if needed.
        """
        for child in children:
            if hasattr(self, child.name) and getattr(self, child.name) == child:
                delattr(self, child.name)

    def _post_attach_children(self, children):
        """ After attaching `children`. We add name attributes associated to the children if there is no attribute of this name.
        """
        for child in children:
            if not hasattr(self, child.name):
                setattr(self, child.name, child)

    def __iadd__(self, assets: Union["Asset", Sequence["Asset"]]):
        if not isinstance(assets, (list, tuple)):
            assets = (assets, )
        self.children += assets
        return self

    def __isub__(self, asset: Union["Asset", Sequence["Asset"]]):
        if not self.children:
            return self
        if not isinstance(assets, (list, tuple)):
            assets = (assets, )
        for asset in assets:
            if asset in self.children:
                children = self.children
                children.remove(asset)
                self.children = children
        return self

    def __repr__(self):
        return f"{self.name} ({self.__class__.__name__})"


class World3D(Asset):
    dimensionality = 3
