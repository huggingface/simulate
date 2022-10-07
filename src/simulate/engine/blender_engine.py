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
import atexit
import base64
import json
import socket
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from ..utils import logging
from .engine import Engine


if TYPE_CHECKING:
    from ..assets.asset import Asset
    from ..scene import Scene


logger = logging.get_logger(__name__)


class BlenderEngine(Engine):
    """
    API to run simulations in the Blender integration.

    Args:
        scene (`Scene`):
            The scene to simulate.
        auto_update (`bool`, *optional*, defaults to `True`):
            Whether to automatically update the scene when an asset is updated.
        start_frame (`int`, *optional*, defaults to `0`):
            The frame to start the simulation at.
        end_frame (`int`, *optional*, defaults to `500`):
            The frame to end the simulation at.
        time_step (`float`, *optional*, defaults to `1.0 / 24.0`):
            The time step of the simulation.
    """

    def __init__(
        self,
        scene: "Scene",
        auto_update: bool = True,
        start_frame: int = 0,
        end_frame: int = 500,
        time_step: float = 1.0 / 24.0,
    ):
        super().__init__(scene=scene, auto_update=auto_update)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.time_step = time_step

        self.host = "127.0.0.1"
        self.port = 55001
        self._initialize_server()
        atexit.register(self._close)

    def _initialize_server(self):
        """Create TCP socket and listen for connections."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        logger.info("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        logger.info(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes_data: bytes, ack: bool) -> str:
        """
        Send bytes to socket and wait for response.

        Args:
            bytes_data (`bytes`):
                The bytes to send.
            ack (`bool`):
                Whether to wait for an acknowledgement.

        Returns:
            response (`bytes`): The response from the socket.
        """
        self.client.sendall(bytes_data)
        if ack:
            return self._get_response()

    def run_command(self, command: Dict, ack: bool = True):
        """Encode command and send the bytes to the socket"""
        message = json.dumps(command)
        logger.info(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self._send_bytes(message_bytes, ack)

    def _get_response(self) -> str:
        """
        Get response from socket.

        Returns:
            response (`str`): The response from the socket.
        """
        while True:
            data_length = self.client.recv(4)
            data_length = int.from_bytes(data_length, "little")

            if data_length:
                response = ""  # TODO: string concatenation may be slow
                while len(response) < data_length:
                    response += self.client.recv(data_length - len(response)).decode()
                return response

    def _send_gltf(self, bytes_data: bytes):
        """
        Send glTF bytes to socket.

        Args:
            bytes_data (`bytes`): The glTF scene as bytes to send.
        """
        b64_bytes = base64.b64encode(bytes_data).decode("ascii")
        command = {"type": "build_scene", "contents": {"b64bytes": b64_bytes}}
        self.run_command(command)

    def update_asset(self, root_node: "Asset"):
        # TODO update and make this API more consistent with all the
        # update_asset_in_scene, recreate_scene, show
        raise NotImplementedError()

    def update_all_assets(self):
        raise NotImplementedError()

    def show(self):
        """Show the scene in Blender."""
        self._send_gltf(self._scene.as_glb_bytes())

    def reset(self):
        """Reset the environment."""
        command = {"type": "reset", "contents": {"message": "message"}}
        self.run_command(command)

    def step(self, action: Optional[Dict] = None, **kwargs: Any) -> Union[Dict, str]:
        raise NotImplementedError()

    def render(self, path: str):
        """
        Render the scene to an image.

        Args:
            path (`str`): The path to save the rendered image to.
        """
        command = {"type": "render", "contents": {"path": path}}
        self.run_command(command)

    def _close(self):
        self.close()

    def close(self):
        """Close the socket."""
        command = {"type": "close", "contents": {"message": "close"}}
        self.run_command(command)
        self.client.close()
        self.socket.close()

        try:
            atexit.unregister(self._close)
        except Exception as e:
            logger.error(f"Exception unregistering close method: {e}")
