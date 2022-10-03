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
""" A simulate Material."""
import copy
import itertools
from dataclasses import dataclass
from typing import ClassVar, List, Optional

import numpy as np
import pyvista

from .utils import camelcase_to_snakecase


class classproperty(object):
    # required to use a classmethod as a property
    # see https://stackoverflow.com/questions/128573/using-property-on-classmethods
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


# This is a very basic PBR Material class, mostly here to be able to load a gltf - strongly base on GLTF definitions
# TODO: Revamp and improve the Material class


@dataclass()
class Material:
    """
    The material appearance of a primitive.

    Parameters
    ----------
    name : string, optional
        The user-defined name of this material

    base_color : np.ndarray or list with 3 (RGB) or 4 (RGBA) components, optional
        The material's base RGB or RGBA color.
        The factors for the base color of the material.
        This value defines linear multipliers for the sampled texels of the base color texture.
        Default: [1,1,1,1]. If provided as RGB, Alpha is assumed to be 1.

    base_color_texture : pyvista.Texture, optional
        A base color texture.
        Can be created from a PIL image, by first converting to a np array and then to a pyvista texture.

    metallic_factor : float, optional
        The metalness of the material.
        Default: 0.0

    roughness_factor : float, optional
        The roughness of the material.
        Default: 1.0

    metallic_roughness_texture : PIL.Image, optional
        The metallic-roughness texture.

    normal_texture : PIL.Image, optional
        The normal map texture.

    occlusion_texture : PIL.Image, optional
        The occlusion map texture.

    emissive_texture : PIL.Image, optional
        The emissive map texture.

    emissive_factor : np.ndarray or list with 3 (RGB) components, optional
        The emissive color of the material.
        Default: [0,0,0]

    alpha_mode : string selected in ["OPAQUE", "MASK" and "BLEND"]
        The alpha rendering mode of the material.
            "OPAQUE": The alpha value is ignored, and the rendered output is fully opaque.
            "MASK": The rendered output is either fully opaque or fully transparent depending on the alpha value
                and the specified alpha_cutoff value.
            "BLEND": The alpha value is used to composite the source and destination areas.
                The rendered output is combined with the background using the normal painting operation
                (i.e. the Porter and Duff over operator).
        Default: "OPAQUE"

    alpha_cutoff: float, optional
        The alpha cutoff value of the material.
        Default: 0.5

    double_sided: boolean, optional
        Specifies whether the material is double-sided.
        Default: false
    """

    __NEW_ID: ClassVar[int] = itertools.count()  # Singleton to count instances of the classes for automatic naming

    base_color: Optional[List[float]] = None
    base_color_texture: Optional[pyvista.Texture] = None
    metallic_factor: Optional[float] = None
    roughness_factor: Optional[float] = None
    metallic_roughness_texture: Optional[pyvista.Texture] = None

    normal_texture: Optional[pyvista.Texture] = None
    occlusion_texture: Optional[pyvista.Texture] = None
    emissive_texture: Optional[pyvista.Texture] = None
    emissive_factor: Optional[List[float]] = None
    alpha_mode: Optional[str] = None
    alpha_cutoff: Optional[float] = None
    double_sided: Optional[bool] = None

    name: Optional[str] = None

    def __post_init__(self):
        # Setup all our default values
        if self.base_color is None:
            self.base_color = [1.0, 1.0, 1.0, 1.0]
        elif isinstance(self.base_color, np.ndarray):
            self.base_color = self.base_color.tolist()
        else:
            self.base_color = list(self.base_color)

        if len(self.base_color) == 3:
            self.base_color = self.base_color + [1.0]

        if self.metallic_factor is None:
            self.metallic_factor = 0.0

        if self.roughness_factor is None:
            self.roughness_factor = 1.0

        if self.emissive_factor is None:
            self.emissive_factor = [0.0, 0.0, 0.0]
        elif isinstance(self.emissive_factor, np.ndarray):
            self.emissive_factor = self.emissive_factor.tolist()
        else:
            self.emissive_factor = list(self.emissive_factor)

        if self.alpha_mode is None:
            self.alpha_mode = "OPAQUE"
        elif not isinstance(self.alpha_mode, str) or self.alpha_mode not in ["OPAQUE", "MASK", "BLEND"]:
            raise ValueError('alpha_mode should be a string selected in ["OPAQUE", "MASK", "BLEND"]')

        if self.alpha_cutoff is None:
            self.alpha_cutoff = 0.5

        if self.double_sided is None:
            self.double_sided = False

        if self.name is None:
            mat_id = next(self.__class__.__NEW_ID)
            self.name = camelcase_to_snakecase(self.__class__.__name__ + f"_{mat_id:02d}")

    def __hash__(self) -> int:
        return id(self)

    def copy(self) -> "Material":
        copy_mat = copy.deepcopy(self)
        mat_id = next(self.__class__.__NEW_ID)
        self.name = camelcase_to_snakecase(self.__class__.__name__ + f"_{mat_id:02d}")
        return copy_mat

    # Various default colors
    @classproperty
    def RED(cls) -> "Material":
        return cls(base_color=[1.0, 0.0, 0.0])

    @classproperty
    def GREEN(cls) -> "Material":
        return cls(base_color=[0.0, 1.0, 0.0])

    @classproperty
    def BLUE(cls) -> "Material":
        return cls(base_color=[0.0, 0.0, 1.0])

    @classproperty
    def CYAN(cls) -> "Material":
        return cls(base_color=[0.0, 1.0, 1.0])

    @classproperty
    def MAGENTA(cls) -> "Material":
        return cls(base_color=[1.0, 0.0, 1.0])

    @classproperty
    def YELLOW(cls) -> "Material":
        return cls(base_color=[1.0, 1.0, 0.0])

    @classproperty
    def BLACK(cls) -> "Material":
        return cls(base_color=[0.0, 0.0, 0.0])

    @classproperty
    def WHITE(cls) -> "Material":
        return cls(base_color=[1.0, 1.0, 1.0])

    @classproperty
    def GRAY(cls) -> "Material":
        return cls.GRAY50

    @classproperty
    def GRAY25(cls) -> "Material":
        return cls(base_color=[0.25, 0.25, 0.25])

    @classproperty
    def GRAY50(cls) -> "Material":
        return cls(base_color=[0.5, 0.5, 0.5])

    @classproperty
    def GRAY75(cls) -> "Material":
        return cls(base_color=[0.75, 0.75, 0.75])

    @classproperty
    def TEAL(cls) -> "Material":
        return cls(base_color=[0.0, 0.5, 0.5])

    @classproperty
    def PURPLE(cls) -> "Material":
        return cls(base_color=[0.5, 0.0, 0.5])

    @classproperty
    def OLIVE(cls) -> "Material":
        return cls(base_color=[0.5, 0.5, 0.0])

    @classproperty
    def TRANSPARENT(cls) -> "Material":
        return cls(base_color=[0.0, 0.0, 0.0, 0.0], alpha_mode="BLEND")
