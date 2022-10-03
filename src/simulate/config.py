from dataclasses import dataclass
from typing import List, Optional

from .assets.gltf_extension import GltfExtensionMixin


@dataclass
class Config(GltfExtensionMixin, gltf_extension_name="HF_config", object_type="scene"):
    """
    A scene simulation configuration object.

    Attributes:
        time_step: The amount of time in seconds to simulate per frame.
            (Optional, default 0.02)
        frame_skip: The number of frames to simulate per step().
            (Optional, default 1)
        return_nodes: Whether to return node data by default from step().
            (Optional, default True)
        return_frames: Whether to return camera rendering by default from step().
            (Optional, default True)
        node_filter: If not None, constrain returned nodes to only the provided node names.
            (Optional, default None)
        camera_filter: If not None, constrain return camera renderings to only the provided camera names.
            (Optional, default None)
        ambient_color: The color for the ambient lighting in the scene.
            (Optional, default Gray30)
        gravity: The 3-dimensional vector to use for gravity.
            (Optional, default [0, -9.81, 0])
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
        self.return_nodes = self.return_nodes or True
        self.return_frames = self.return_frames or True
        self.ambient_color = self.ambient_color or [0.329412, 0.329412, 0.329412]
        self.gravity = self.gravity or [0, -9.81, 0]
