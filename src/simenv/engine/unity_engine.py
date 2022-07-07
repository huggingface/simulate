import atexit
import base64
import json
import socket
import subprocess

import numpy as np

from simenv.rl.components import RlComponent

from .engine import Engine


PRIMITIVE_TYPE_MAPPING = {
    "Sphere": 0,
    "Capsule": 1,
    "Cylinder": 2,
    "Box": 3,
    "Plane": 4,
    "Quad": 5,
}


class UnityEngine(Engine):
    def __init__(
        self,
        scene,
        auto_update=True,
        start_frame=0,
        end_frame=500,
        frame_rate=24,
        engine_exe=None,
        engine_headless=None,
        engine_port=55000,
        physics_update_rate=30.0,
        frame_skip=15,
    ):
        super().__init__(scene=scene, auto_update=auto_update)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate

        self.action_space = None
        self.observation_space = None

        self.host = "127.0.0.1"
        self.port = engine_port

        if engine_exe is not None:
            self._launch_executable(engine_exe, engine_port, engine_headless, physics_update_rate, frame_skip)

        self._initialize_server()
        atexit.register(self._close)

        self._map_pool = False

    def _launch_executable(self, executable, port, headless, physics_update_rate, frame_skip):
        # TODO: improve headless training check on a headless machine
        if headless:
            print("launching env headless")
            launch_command = f"{executable} -batchmode -nographics --args port {port} \
                physics_update_rate {physics_update_rate} frame_skip {frame_skip}".split(
                " "
            )
        else:
            launch_command = f"{executable} --args port {port} \
                physics_update_rate {physics_update_rate} frame_skip {frame_skip}".split(
                " "
            )
        self.proc = subprocess.Popen(
            launch_command,
            start_new_session=False,
        )

    def _initialize_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        print("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        print(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes, ack):
        self.client.sendall(bytes)
        if ack:
            return self._get_response()

    def _get_response(self):
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
        self.run_command(command, ack=True)

    def update_asset(self, root_node):
        # TODO update and make this API more consistent with all the
        # update_asset, update, show
        pass

    def update_all_assets(self):
        pass

    def show(self, n_maps=-1, **engine_kwargs):
        if self._map_pool:
            self._send_gltf(self._scene.as_glb_bytes())
            self._activate_pool(n_maps=n_maps)
        else:
            self.add_to_pool(self._scene)
            self._activate_pool(n_maps=1)

    def _activate_pool(self, n_maps):
        command = {"type": "ActivateEnvironments", "contents": json.dumps({"n_maps": n_maps})}
        return self.run_command(command)

    def add_to_pool(self, map):
        self._map_pool = True
        agent = map.tree_filtered_descendants(lambda node: isinstance(node.rl_component, RlComponent))[0]
        self.action_space = agent.action_space
        self.observation_space = agent.observation_space

        map_bytes = map.as_glb_bytes()
        b64_bytes = base64.b64encode(map_bytes).decode("ascii")
        command = {"type": "AddToPool", "contents": json.dumps({"b64bytes": b64_bytes})}
        self.run_command(command, ack=True)

    def step(self, action=None):
        command = {"type": "Step", "contents": json.dumps({"action": action})}
        return self.run_command(command)

    def step_send(self, action):
        command = {"type": "Step", "contents": json.dumps({"action": action})}
        return self.run_command(command, ack=False)

    def step_recv(self):
        return self._get_response()

    def get_reward(self):
        command = {"type": "GetReward", "contents": json.dumps({"message": "message"})}
        response = self.run_command(command)
        data = json.loads(response)
        return [float(f) for f in data["Items"]]

    def get_reward_send(self):
        command = {"type": "GetReward", "contents": json.dumps({"message": "message"})}
        self.run_command(command, ack=False)

    def get_reward_recv(self):
        response = self._get_response()
        data = json.loads(response)
        return [float(f) for f in data["Items"]]

    def get_done(self):
        command = {"type": "GetDone", "contents": json.dumps({"message": "message"})}
        response = self.run_command(command)
        data = json.loads(response)
        return [d for d in data["Items"]]

    def get_done_send(self):
        command = {"type": "GetDone", "contents": json.dumps({"message": "message"})}
        self.run_command(command, ack=False)

    def get_done_recv(self):
        response = self._get_response()
        data = json.loads(response)
        return [d for d in data["Items"]]

    def reset(self):
        command = {"type": "Reset", "contents": json.dumps({"message": "message"})}
        self.run_command(command)

    def reset_send(self):
        command = {"type": "Reset", "contents": json.dumps({"message": "message"})}
        self.run_command(command, ack=False)

    def reset_recv(self):
        return self._get_response()

    def get_obs(self):
        command = {"type": "GetObservation", "contents": json.dumps({"message": "message"})}
        encoded_obs = self.run_command(command)
        data = json.loads(encoded_obs)
        decoded_obs = self._reshape_obs(data)
        return decoded_obs

    def get_observation_send(self):
        command = {"type": "GetObservation", "contents": json.dumps({"message": "message"})}
        self.run_command(command, ack=False)

    def get_observation_recv(self):
        encoded_obs = self._get_response()
        data = json.loads(encoded_obs)
        decoded_obs = self._reshape_obs(data)
        return decoded_obs

    def _reshape_obs(self, obs):
        # TODO: remove np.flip for training (the agent does not care the world is upside-down
        # TODO: have unity side send in B,C,H,W order
        shape = obs["shape"]
        return np.flip(np.array(obs["Items"]).astype(np.uint8).reshape(*shape), 1).transpose(0, 3, 1, 2)

    def render(self, path: str):
        command = {"type": "Render", "contents": json.dumps({"path": path})}
        self.run_command(command)

    def run_command(self, command, ack=True):
        message = json.dumps(command)
        # print(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self._send_bytes(message_bytes, ack)

    def _close(self):
        # print("exit was not clean, using atexit to close env")
        self.close()

    def close(self):
        command = {"type": "Close", "contents": json.dumps({"message": "close"})}
        try:
            self.run_command(command)
        except Exception as e:
            print("exception sending close message", e)

        print("closing client")
        self.client.close()

        try:
            atexit.unregister(self._close)
        except Exception as e:
            print("exception unregistering close method", e)
