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
""" A fast integrated backend for massively paralleled observations rendering. """
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

import numpy as np
import raylib
import pybullet

from ..assets import Asset, Camera, Light, Material, Object3D
from ..utils import logging
from .engine import Engine


if TYPE_CHECKING:
    from ..assets.asset import Asset
    from ..scene import Scene


class FastEngine(Engine):
    def __init__(
        self,
        scene: "Scene",
        auto_update: bool = True,
        engine_headless: bool = False,
    ):
        super().__init__(scene, auto_update)
        self.headless = engine_headless

    def show(self):
        if not self.headless:
            raylib.InitWindow(1600, 900, "Simulate")
            self._render()

    def step(self):
        self._render()

    def _render(self):
        raylib.BeginDrawing()
        raylib.ClearBackground(raylib.BLACK)

        raylib.EndDrawing()

    def close(self):
        """Close the scene."""
        raylib.CloseWindow()
