import atexit
import base64
import json
import socket
import subprocess

from ..gltf_export import tree_as_glb_bytes
from .engine import Engine


PRIMITIVE_TYPE_MAPPING = {
    "Sphere": 0,
    "Capsule": 1,
    "Cylinder": 2,
    "Cube": 3,
    "Plane": 4,
    "Quad": 5,
}


class UnityEngine:
    def __init__(self, scene, auto_update=True, executable=None, headless=None, start_frame=0, end_frame=500, frame_rate=24, port=55000):
        super().__init__(scene=scene, auto_update=auto_update)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate

        self.host = "127.0.0.1"
        self.port = port

        if executable is not None:
            self._launch_executable(executable, port, headless)

        self._initialize_server()
        atexit.register(self._close)
        
        
    def _launch_executable(self, executable, port, headless):

        if headless:
            print("launching env headless")
            launch_command = f"{executable} -batchmode -nographics --args port {port}".split(" ")
        else:
            launch_command = f"{executable} --args port {port}".split(" ")
        self.proc = subprocess.Popen(
            launch_command,
            start_new_session=False,
        )

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
            data_length = self.client.recv(4)
            data_length = int.from_bytes(data_length, "little")

            if data_length:
                response = ""  # TODO: string concatenation may be slow
                while len(response) < data_length:
                    response += self.client.recv(data_length - len(response)).decode()

                # print(f"Received response: {response}")
                return response

    def _send_gltf(self, bytes):
        b64_bytes = base64.b64encode(bytes).decode("ascii")
        command = {"type": "BuildScene", "contents": json.dumps({"b64bytes": b64_bytes})}
        self.run_command(command)

    def update_asset(self, root_node):
        # TODO update and make this API more consistent with all the
        # update_asset, update, show
        pass

    def update_all_assets(self):
        pass

    def show(self, **engine_kwargs):
        self._send_gltf(tree_as_glb_bytes(self._scene))

    def step(self, action):
        command = {"type": "Step", "contents": json.dumps({"action": action})}
        return self.run_command(command)

    def get_reward(self):
        command = {"type": "GetReward", "contents": json.dumps({"message": "message"})}
        return float(self.run_command(command))

    def get_done(self):
        command = {"type": "GetDone", "contents": json.dumps({"message": "message"})}

        return self.run_command(command) == "True"

    def reset(self):
        command = {"type": "Reset", "contents": json.dumps({"message": "message"})}
        self.run_command(command)

    def get_observation(self):
        command = {"type": "GetObservation", "contents": json.dumps({"message": "message"})}

        encoded_obs = self.run_command(command)
        decoded_obs = json.loads(encoded_obs)

        return decoded_obs

    def run_command(self, command):
        message = json.dumps(command)
        # print(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self._send_bytes(message_bytes)

    def _close(self):
        # print("exit was not clean, using atexit to close env")
        self.close()

    def close(self):
        command = {"type": "Close", "contents": json.dumps({"message": "close"})}
        self.run_command(command)
        self.client.close()

        try:
            atexit.unregister(self._close)
        except Exception as e:
            print("exception unregistering close method", e)
