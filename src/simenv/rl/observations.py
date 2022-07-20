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
""" Some mapping from Discrete and Box Spaces to physics actions."""
import numpy as np

from ..assets.asset import Asset
from ..assets.camera import Camera


try:
    from gym import spaces
except ImportError:
    spaces = None


def map_observation_devices_to_spaces(asset: Asset):
    if isinstance(asset, Camera):
        if spaces is None:
            raise ImportError("gym is not installed. Please install gym to use the RL agent.")
        return spaces.Box(low=0, high=255, shape=[3, asset.height, asset.width], dtype=np.uint8)
    raise NotImplementedError(
        f"This Asset ({type(Asset)})is not yet implemented " f"as an RlAgent type of observation."
    )
