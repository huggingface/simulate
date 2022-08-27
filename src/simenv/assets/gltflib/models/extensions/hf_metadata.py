from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Metadata:
    """
    A serialization of initialization metadata. These parameters can be overridden as keywords in show().

    Attributes:
        frame_rate: Number of frames per second to use for simulation. (Optional, default 30)
        frame_skip: The number of frames to simulate per step(). (Optional, default 1)
        return_nodes: Whether to return node data by default from step(). (Optional, default True)
        return_frames: Whether to return camera rendering by default from step(). (Optional, default True)
        node_filter: If not None, constrain returned nodes to only the provided node names. (Optional, default None)
        camera_filter: If not None, constrain return camera renderings to only the provided camera names. (Optional, default None)
        ambient_color: The color for the ambient lighting in the scene. (Optional, default Gray30)
    """

    frame_rate: Optional[int] = None
    frame_skip: Optional[int] = None
    return_nodes: Optional[bool] = None
    return_frames: Optional[bool] = None
    node_filter: Optional[List[str]] = None
    camera_filter: Optional[List[str]] = None
    ambient_color: Optional[List[float]] = None
