import base64
import json
import socket

from ..gltf_export import tree_as_glb_bytes


PRIMITIVE_TYPE_MAPPING = {
    "Sphere": 0,
    "Capsule": 1,
    "Cylinder": 2,
    "Cube": 3,
    "Plane": 4,
    "Quad": 5,
}


class UnityEngine:
    def __init__(self, scene, start_frame=0, end_frame=500, frame_rate=24):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate
        self._scene = scene

        self.host = "127.0.0.1"
        self.port = 55000
        self._initialize_server()

    def _initialize_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        print("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        print(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes):
        self.client.sendall(bytes)
        while True:
            data = self.client.recv(65535)
            if data:
                response = data.decode()
                print(f"Received response: {response}")
                return response

    def _send_gltf(self, bytes):
        b64_bytes = base64.b64encode(bytes).decode("ascii")
        command = {"type": "BuildScene", "contents": json.dumps({"b64bytes": b64_bytes})}
        self.run_command(command)

    def update_asset_in_scene(self, root_node):
        # TODO update and make this API more consistent with all the
        # update_asset_in_scene, recreate_scene, show
        self._send_gltf(tree_as_glb_bytes(self._scene))

    def recreate_scene(self):
        self._send_gltf(tree_as_glb_bytes(self._scene))

    def show(self):
        self._send_gltf(tree_as_glb_bytes(self._scene))

    def step(self, action):
        command = {"type": "Step", "contents": json.dumps({"action": action})}
        self.run_command(command)

    def run_command(self, command):
        message = json.dumps(command)
        print(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        self._send_bytes(message_bytes)

    def close(self):
        self.client.close()
