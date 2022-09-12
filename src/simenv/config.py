from dataclasses import dataclass
from typing import List, Optional

from .assets.gltf_extension import GltfExtensionMixin


@dataclass
class Config(GltfExtensionMixin, gltf_extension_name="HF_config", object_type="scene"):
    """
    A scene simulation configuration object.

    Attributes:
        frame_rate: Number of frames per second to use for simulation. (Optional, default 30)
        frame_skip: The number of frames to simulate per step(). (Optional, default 1)
        return_nodes: Whether to return node data by default from step(). (Optional, default True)
        return_frames: Whether to return camera rendering by default from step(). (Optional, default True)
        node_filter: If not None, constrain returned nodes to only the provided node names. (Optional, default None)
        camera_filter: If not None, constrain return camera renderings to only the provided camera names. (Optional, default None)
        ambient_color: The color for the ambient lighting in the scene. (Optional, default Gray30)
        gravity: The 3-dimensional vector to use for gravity. (Optional, default [0, -9.81, 0])
    """

    frame_rate: Optional[int] = None
    frame_skip: Optional[int] = None
    return_nodes: Optional[bool] = None
    return_frames: Optional[bool] = None
    node_filter: Optional[List[str]] = None
    camera_filter: Optional[List[str]] = None
    ambient_color: Optional[List[float]] = None
    gravity: Optional[List[float]] = None
