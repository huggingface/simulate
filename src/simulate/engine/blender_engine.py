import atexit
import base64
import json
import socket
from typing import TYPE_CHECKING, Any, Dict, Optional

from ..utils import logging
from .engine import Engine


if TYPE_CHECKING:
    from ..assets.asset import Asset
    from ..scene import Scene


logger = logging.get_logger(__name__)


class BlenderEngine(Engine):
    """API for the Blender integration"""

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
        """Create TCP socket and listen for connections"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        logger.info("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        logger.info(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes_data: bytes, ack: bool) -> Optional[str]:
        """Send bytes to socket and wait for response"""
        self.client.sendall(bytes_data)
        if ack:
            return self._get_response()

    def _get_response(self) -> str:
        """Get response from socket"""
        while True:
            data_length = self.client.recv(4)
            data_length = int.from_bytes(data_length, "little")

            if data_length:
                response = ""  # TODO: string concatenation may be slow
                while len(response) < data_length:
                    response += self.client.recv(data_length - len(response)).decode()
                return response

    def _send_gltf(self, bytes_data: bytes):
        """Send gltf bytes to socket"""
        b64_bytes = base64.b64encode(bytes_data).decode("ascii")
        command = {"type": "build_scene", "contents": {"b64bytes": b64_bytes}}
        self.run_command(command)

    def run_command(self, command: Dict, ack: bool = True):
        """Encode command and send the bytes to the socket"""
        message = json.dumps(command)
        logger.info(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self._send_bytes(message_bytes, ack)

    def update_asset(self, root_node: "Asset"):
        # TODO update and make this API more consistent with all the
        # update_asset_in_scene, recreate_scene, show
        raise NotImplementedError()

    def update_all_assets(self):
        raise NotImplementedError()

    def show(self):
        """Show the scene in Blender"""
        self._send_gltf(self._scene.as_glb_bytes())

    def reset(self):
        """Reset the environment"""
        command = {"type": "reset", "contents": {"message": "message"}}
        self.run_command(command)

    def step(self, action: Optional[Dict] = None, **kwargs: Any):
        raise NotImplementedError()

    def render(self, path: str):
        """Render the scene to an image"""
        command = {"type": "render", "contents": {"path": path}}
        self.run_command(command)

    def _close(self):
        self.close()

    def close(self):
        """Close the environment"""
        command = {"type": "close", "contents": {"message": "close"}}
        self.run_command(command)
        self.client.close()

        try:
            atexit.unregister(self._close)
        except Exception as e:
            logger.error(f"Exception unregistering close method: {e}")
