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
""" Some predefined RGB colors."""
import numpy as np


BLACK = (0.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
CYAN = (0.0, 1.0, 1.0)
GRAY25 = (0.25, 0.25, 0.25)
GRAY50 = (0.5, 0.5, 0.5)
GRAY75 = (0.75, 0.75, 0.75)
GRAY = GRAY50
GREEN = (0.0, 1.0, 0.0)
MAGENTA = (1.0, 0.0, 1.0)
OLIVE = (0.5, 0.5, 0.0)
PURPLE = (0.5, 0.0, 0.5)
RED = (1.0, 0.0, 0.0)
TEAL = (0.0, 0.5, 0.5)
WHITE = (1.0, 1.0, 1.0)
YELLOW = (1.0, 1.0, 0.0)

COLORS_ALL = {
    "BLACK": BLACK,
    "BLUE": BLUE,
    "CYAN": CYAN,
    "GRAY25": GRAY25,
    "GRAY50": GRAY50,
    "GRAY75": GRAY75,
    "GRAY": GRAY,
    "GREEN": GREEN,
    "MAGENTA": MAGENTA,
    "OLIVE": OLIVE,
    "PURPLE": PURPLE,
    "RED": RED,
    "TEAL": TEAL,
    "WHITE": WHITE,
    "YELLOW": YELLOW,
}

COLORS_NO_GRAYSCALE = {
    "BLUE": BLUE,
    "CYAN": CYAN,
    "GREEN": GREEN,
    "MAGENTA": MAGENTA,
    "OLIVE": OLIVE,
    "PURPLE": PURPLE,
    "RED": RED,
    "TEAL": TEAL,
    "YELLOW": YELLOW,
}

COLORS_ONLY_GRAYSCALE = {
    "WHITE": WHITE,
    "GRAY25": GRAY25,
    "GRAY50": GRAY50,
    "GRAY75": GRAY75,
    "GRAY100": BLACK,
}

CMAP_ALL = np.array([list(COLORS_ALL.values())] * 2)  # Final shape: (2, len(colors), 3) for (U, V, RGB)
CMAP_3_COLORS = np.array([[GREEN, GREEN]] * 2)  # Final shape: (2, len(colors), 3) for (U, V, RGB)
CMAP_ONLY_COLORS = np.array(
    [list(COLORS_NO_GRAYSCALE.values())] * 2
)  # Final shape: (2, len(colors), 3) for (U, V, RGB)
CMAP_ONLY_GRAYSCALE = np.array(
    [list(COLORS_ONLY_GRAYSCALE.values())] * 2
)  # Final shape: (2, len(colors), 3) for (U, V, RGB)

TEXTURES_ALL = {
    "cmap_all": CMAP_ALL,
    "cmap_3_colors": CMAP_3_COLORS,
    "cmap_only_colors": CMAP_ONLY_COLORS,
    "cmap_only_grayscale": CMAP_ONLY_GRAYSCALE,
}
