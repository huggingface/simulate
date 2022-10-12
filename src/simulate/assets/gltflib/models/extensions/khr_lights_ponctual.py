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
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class KHRLightsPunctualLight:
    """
    A punctual light source within a scene. This extension defines three "punctual" light types:
    directional, point and spot.
    Punctual lights are defined as parameterized, infinitely small points that emit light
    in well-defined directions and intensities.
    A node can reference a light to apply a transform to place the light in the scene.

    Properties:
    color (number [3]): RGB value for light's color in linear space.
        (Optional, default: [1.0, 1.0, 1.0])
    intensity (float) Brightness of light in. The units that this is defined in depend on the type of light.
        point and spotlights use luminous intensity in candela (lm/sr)
        while directional lights use illuminance in lux (lm/m2)
        (Optional)
    type (string) Declares the type of the light (directional, point or spot). (Required)
    name (string) The user-defined name of this object. (Optional)
    range (float) Hint defining a distance cutoff at which the light's intensity may be considered to have reached zero.
        Supported only for point and spotlights. Must be > 0. When undefined, range is assumed to be infinite.
        (Optional)
    """

    color: Optional[List[float]] = None
    intensity: float = 1.0
    type: Optional[str] = None
    range: Optional[float] = None
    innerConeAngle: float = 0.0
    outerConeAngle: float = np.pi / 4.0
    name: Optional[str] = None


@dataclass_json
@dataclass
class KHRLightsPunctual:
    """
    A punctual light source within a scene. This extension defines three "punctual" light types:
    directional, point and spot.
    Punctual lights are defined as parameterized, infinitely small points that emit light
    in well-defined directions and intensities.
    A node can reference a light to apply a transform to place the light in the scene.

    Properties:
    lights (list) Array of lights
    """

    lights: Optional[List[KHRLightsPunctualLight]] = None
    light: Optional[int] = None
