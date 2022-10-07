# Copyright 2022 The HuggingFace Authors.
# Copyright (c) 2019 Sergey Krilov
# Copyright (c) 2018 Luke Miller
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Lint as: python3
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from .animation_sampler import AnimationSampler
from .channel import Channel
from .named_base_model import NamedBaseModel


@dataclass_json
@dataclass
class Animation(NamedBaseModel):
    """
    A keyframe animation.

    Properties:
    channels (channel [1-*]) An array of channels, each of which targets an animation's sampler at a node's property.
        Different channels of the same animation can't have equal targets. (Required)
    samplers (AnimationSampler[1-*]) An array of samplers that combines input and output accessors with an interpolation
        algorithm to define a keyframe graph (but not its target). (Required)
    name (string): The user-defined name of this object. (Optional)
    extensions (object): Dictionary object with extension-specific objects. (Optional)
    extras (any): Application-specific data. (Optional)
    """

    channels: Optional[List[Channel]] = None
    samplers: Optional[List[AnimationSampler]] = None
