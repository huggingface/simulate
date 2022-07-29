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
""" Some shortcut for textures."""
import numpy as np
import pyvista as pv

from .colors import CMAP_ONLY_COLORS


# class Texture(pv.Texture):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#     @classproperty
#     def TEXTURE_1D_CMAP(cls) -> "Texture":
#         return cls.from_pyvista(pv.numpy_to_texture(CMAP_ONLY_COLORS[:, np.newaxis, :]))

TEXTURE_1D_CMAP = pv.numpy_to_texture(CMAP_ONLY_COLORS[:, np.newaxis, :])


def texture_from_1d_cmap(np_array: np.array) -> pv.Texture:
    return pv.numpy_to_texture(np_array[:, np.newaxis, :])
