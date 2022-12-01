# Copyright 2020 Optuna, Hugging Face
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
""" Import utilities."""

import importlib.util


_vhacd_available = importlib.util.find_spec("simulate._vhacd") is not None
_fastwfc_available = importlib.util.find_spec("simulate._fastwfc") is not None


def is_vhacd_available():
    return _vhacd_available


def is_fastwfc_available():
    return _fastwfc_available
