import atexit
import base64
import json
import socket

from .engine import Engine


class BlenderEngine(Engine):
    """API for the Blender integration"""

    def __init__(self, scene, auto_update=True, start_frame=0, end_frame=500, frame_rate=24):
        super().__init__(scene=scene, auto_update=auto_update)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate

        self.host = "127.0.0.1"
        self.port = 55000
        self._initialize_server()
        atexit.register(self._close)

    def _initialize_server(self):
        """Create TCP socket and listen for connections"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        print("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        print(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes, ack):
        """Send bytes to socket and wait for response"""
        self.client.sendall(bytes)
        if ack:
            return self._get_response()

    def _get_response(self):
        """Get response from socket"""
        while True:
            data_length = self.client.recv(4)
            data_length = int.from_bytes(data_length, "little")

            if data_length:
                response = ""  # TODO: string concatenation may be slow
                while len(response) < data_length:
                    response += self.client.recv(data_length - len(response)).decode()
                return response

    def _send_gltf(self, bytes):
        """Send gltf bytes to socket"""
        b64_bytes = base64.b64encode(bytes).decode("ascii")
        command = {"type": "build_scene", "contents": {"b64bytes": b64_bytes}}
        self.run_command(command)

    def run_command(self, command, ack=True):
        """Encode command and send the bytes to the socket"""
        message = json.dumps(command)
        print(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self._send_bytes(message_bytes, ack)

    def update_asset(self, root_node):
        # TODO update and make this API more consistent with all the
        # update_asset_in_scene, recreate_scene, show
        pass

    def update_all_assets(self):
        pass

    def show(self, **engine_kwargs):
        """Show the scene in Blender"""
        self._send_gltf(self._scene.as_glb_bytes())

    def reset(self):
        """Reset the environment"""
        command = {"type": "reset", "contents": {"message": "message"}}
        self.run_command(command)

    def render(self, path: str, **engine_kwargs):
        """Render the scene to an image"""
        command = {"type": "render", "contents": {"path": path}}
        self.run_command(command)

    def _close(self):
        # print("exit was not clean, using atexit to close env")
        self.close()

    def close(self):
        """Close the environment"""
        command = {"type": "close", "contents": {"message": "close"}}
        self.run_command(command)
        self.client.close()

        try:
            atexit.unregister(self._close)
        except Exception as e:
            print("exception unregistering close method", e)
