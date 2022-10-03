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
