import atexit
import base64
import json
import socket
from typing import TYPE_CHECKING, Any, Dict, Union

from ..utils import logging
from .engine import Engine


if TYPE_CHECKING:
    from ..assets.asset import Asset
    from ..scene import Scene


logger = logging.get_logger(__name__)


class GodotEngine(Engine):
    """API for the Godot 4 engine integration"""

    def __init__(
        self,
        scene: "Scene",
        auto_update: bool = True,
        start_frame: int = 0,
        end_frame: int = 500,
        time_step: float = 1 / 24.0,
        engine_port: int = 55001,
    ):
        super().__init__(scene=scene, auto_update=auto_update)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.time_step = time_step

        self.action_space = None
        self.observation_space = None

        self.host = "127.0.0.1"
        self.port = engine_port
        self._initialize_server()
        atexit.register(self._close)

        self._map_pool = False

    def _initialize_server(self):
        """Create TCP socket and listen for connections"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        logger.info("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        logger.info(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes_data: bytes, ack: bool):
        """Send bytes to socket and wait for response"""
        self.client.sendall(bytes_data)
        if ack:
            return self._get_response()

    def run_command(self, command: str, **kwargs: Any) -> Union[Dict, str]:
        """Encode command and send the bytes to the socket"""
        message = json.dumps({"type": command, **kwargs})
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        self.client.sendall(message_bytes)
        response = self._get_response()
        try:
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Exception loading response json data: {e}")
            return response

    def run_command_async(self, command: str, **kwargs: Any):
        message = json.dumps({"type": command, **kwargs})
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        self.client.sendall(message_bytes)

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

    def get_response_async(self) -> Union[Dict, str]:
        response = self._get_response()
        try:
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Exception loading response json data: {e}")
            return response

    def show(self, **kwargs: Any) -> Union[Dict, str]:
        """Show the scene in Godot"""
        bytes_data = self._scene.as_glb_bytes()
        b64bytes = base64.b64encode(bytes_data).decode("ascii")
        kwargs.update({"b64bytes": b64bytes})
        return self.run_command("initialize", **kwargs)

    def update_asset(self, root_node: "Asset"):
        # TODO update and make this API more consistent with all the
        # update_asset_in_scene, recreate_scene, show
        raise NotImplementedError()

    def update_all_assets(self):
        raise NotImplementedError()

    def step(self, **kwargs: Any) -> Union[Dict, str]:
        """Step the simulation"""
        return self.run_command("step", **kwargs)

    def reset(self) -> Union[Dict, str]:
        """Reset the environment"""
        return self.run_command("reset")

    def _close(self):
        self.close()

    def close(self):
        """Close the environment"""
        try:
            self.run_command("close")
        except Exception as e:
            logger.error(f"Exception sending close message: {e}")
        self.client.close()
        try:
            atexit.unregister(self._close)
        except Exception as e:
            logger.error(f"Exception unregistering close method: {e}")
