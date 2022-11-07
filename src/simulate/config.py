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

from .assets.gltf_extension import GltfExtensionMixin


@dataclass
class Config(GltfExtensionMixin, gltf_extension_name="HF_config", object_type="scene"):
    """
    A scene simulation configuration object.

    Args:
        time_step (`float`, *optional*, defaults to `0.02`):
            The amount of time in seconds to simulate per frame.
        frame_skip (`int`, *optional*, defaults to `1`):
            The number of frames to simulate per step().
        return_nodes (`bool`, *optional*, defaults to `True`):
            Whether to return node data by default from step().
        return_frames (`bool`, *optional*, defaults to `True`):
            Whether to return camera rendering by default from step().
        node_filter (`List[str]`, *optional*, defaults to `None`):
            If not None, constrain returned nodes to only the provided node names.
        camera_filter (`List[str]`, *optional*, defaults to `None`):
            If not None, constrain return camera renderings to only the provided camera names.
        ambient_color (`List[float]`, *optional*, defaults to `Gray30`):
            The color for the ambient lighting in the scene.
        gravity (`List[float]`, *optional*, defaults to `[0, -9.81, 0]`):
            The 3-dimensional vector to use for gravity.
    """

    time_step: Optional[float] = None
    frame_skip: Optional[int] = None
    return_nodes: Optional[bool] = None
    return_frames: Optional[bool] = None
    node_filter: Optional[List[str]] = None
    camera_filter: Optional[List[str]] = None
    ambient_color: Optional[List[float]] = None
    gravity: Optional[List[float]] = None

    def __post_init__(self):
        self.time_step = self.time_step or 0.02
        self.frame_skip = self.frame_skip or 1
        if self.return_nodes is None:
            self.return_nodes = True
        if self.return_frames is None:
            self.return_frames = True
        self.ambient_color = self.ambient_color or [0.329412, 0.329412, 0.329412]
        self.gravity = self.gravity or [0, -9.81, 0]
