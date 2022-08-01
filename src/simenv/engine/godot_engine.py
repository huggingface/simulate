import atexit
import base64
import json
import socket
import numpy as np

from simenv.rl.rl_component import RlComponent
from .engine import Engine


class GodotEngine(Engine):
    def __init__(self, scene, auto_update=True, start_frame=0, end_frame=500, frame_rate=24, engine_port=55000):
        super().__init__(scene=scene, auto_update=auto_update)
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate

        self.action_space = None
        self.observation_space = None

        self.host = "127.0.0.1"
        self.port = engine_port
        self._initialize_server()
        atexit.register(self._close)

        self._map_pool = False

    def _initialize_server(self):
        """Create TCP socket and listen for connections."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        print("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        print(f"Connection from {self.client_address}")

    def _send_bytes(self, bytes, ack):
        """Send bytes to server and wait for response."""
        self.client.sendall(bytes)
        if ack:
            return self._get_response()

    def _get_response(self):
        """Get response from server."""
        while True:
            data_length = self.client.recv(4)
            data_length = int.from_bytes(data_length, "little")

            if data_length:
                response = ""  # TODO: string concatenation may be slow
                while len(response) < data_length:
                    response += self.client.recv(data_length - len(response)).decode()
                return response

    def _send_gltf(self, bytes):
        """Send gltf bytes to server."""
        b64_bytes = base64.b64encode(bytes).decode("ascii")
        command = {"type": "BuildScene", "contents": {"b64bytes": b64_bytes}}
        self.run_command(command)

    def update_asset(self, root_node):
        # TODO update and make this API more consistent with all the
        # update_asset_in_scene, recreate_scene, show
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
        self._send_gltf(self._scene.as_glb_bytes())

    def _activate_pool(self, n_maps):
        command = {"type": "ActivateEnvironments", "contents": {"n_maps": n_maps}}
        return self.run_command(command)

    def add_to_pool(self, map):
        self._map_pool = True
        agent = map.tree_filtered_descendants(lambda node: isinstance(node.rl_component, RlComponent))[0]
        self.action_space = agent.acton_space
        self.observation_space = agent.observation_space
        map_bytes = map.as_glb_bytes()
        b64_bytes = base64.b64encode(map_bytes).decode("ascii")
        command = {"type": "AddToPool", "contents": {"b64bytes": b64_bytes}}
        self.run_command(command, ack=True)

    def step(self, action=None):
        command = {"type": "Step", "contents": {"action": action}}
        return self.run_command(command)

    def step_send(self, action):
        command = {"type": "Step", "contents": {"action": action}}
        self.run_command(command, ack=False)

    def step_recv(self):
        return self._get_response()

    def get_reward(self):
        command = {"type": "GetReward", "contents": {"message": "message"}}
        response = self.run_command(command)
        data = json.loads(response)
        return [float(f) for f in data["Items"]]

    def get_reward_send(self):
        command = {"type": "GetReward", "contents": {"message": "message"}}
        return self.run_command(command, ack=False)

    def get_reward_recv(self):
        response = self._get_response()
        data = json.loads(response)
        return [float(f) for f in data["Items"]]

    def get_done(self):
        command = {"type": "GetDone", "contents": {"message": "message"}}
        response = self.run_command(command)
        data = json.loads(response)
        return [d for d in data["Items"]]

    def get_done_send(self):
        command = {"type": "GetDone", "contents": {"message": "message"}}
        self.run_command(command, ack=False)

    def get_done_recv(self):
        response = self._get_response()
        data = json.loads(response)
        return [d for d in data["Items"]]

    def reset(self):
        command = {"type": "Reset", "contents": {"message": "message"}}
        self.run_command(command)

    def reset_send(self):
        command = {"type": "Reset", "contents": {"message": "message"}}
        self.run_command(command, ack=False)

    def reset_recv(self):
        return self._get_response()

    def get_obs(self):
        command = {"type": "GetObservation", "contents": {"message": "message"}}
        encoded_obs = self.run_command(command)
        data = json.loads(encoded_obs)
        decoded_obs = self._extract_sensor_obs(data)
        return decoded_obs

    def get_observation_send(self):
        command = {"type": "GetObservation", "contents": {"message": "message"}}
        self.run_command(command, ack=False)

    def get_observation_recv(self):
        encoded_obs = self._get_response()
        data = json.loads(encoded_obs)
        decoded_obs = self._extract_sensor_obs(data)
        return decoded_obs

    def _extract_sensor_obs(self, data):
        sensor_obs = {}
        for obs_json in data["Items"]:
            obs_data = json.loads(obs_json)
            name = obs_data["name"]
            sensor_obs[name] = self._reshape_obs(obs_data)
        return sensor_obs

    def _reshape_obs(self, obs):
        shape = obs["shape"]
        if len(shape) < 2:
            return np.array(obs["Items"]).astype(np.float32).reshape(*shape)
        else:
            return np.flip(np.array(obs["Items"]).astype(np.uint8).reshape(*shape), 1).transpose(0, 3, 1, 2)

    def run_command(self, command, ack=True):
        message = json.dumps(command)
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self._send_bytes(message_bytes, ack)

    def _close(self):
        self.close()

    def close(self):
        command = {"type": "Close", "contents": json.dumps({"message": "close"})}
        self.run_command(command)
        self.client.close()
        try:
            atexit.unregister(self._close)
        except Exception as e:
            print("exception unregistering close method", e)
