import base64
import json
import socket

import numpy as np


PRIMITIVE_TYPE_MAPPING = {
    "Sphere": 0,
    "Capsule": 1,
    "Cylinder": 2,
    "Cube": 3,
    "Plane": 4,
    "Quad": 5,
}


class Unity:
    def __init__(self, scene, start_frame=0, end_frame=500, frame_rate=24):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate

        self.host = "127.0.0.1"
        self.port = 55000
        self.initialize_server()

    def initialize_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        print("Server started. Waiting for connection...")
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        print(f"Connection from {self.client_address}")

    def send_bytes(self, bytes):
        self.client.sendall(bytes)
        while True:
            data = self.client.recv(65535)
            if data:
                response = data.decode()
                print(f"Received response: {response}")
                return response

    def send_gltf(self, bytes):
        b64_bytes = base64.b64encode(bytes).decode("ascii")
        command = {"type": "BuildScene", "contents": json.dumps({"b64bytes": b64_bytes})}
        self.run_command(command)

    def step(self, action):
        command = {"type": "Step", "contents": json.dumps({"action": action})}
        return self.run_command(command)

    def get_observation(self):
        command = {"type": "GetObservation", "contents": json.dumps({"message": "message"})}

        encoded_obs = self.run_command(command)
        decoded_obs = json.loads(encoded_obs)

        return decoded_obs

    def run_command(self, command):
        message = json.dumps(command)
        print(f"Sending command: {message}")
        message_bytes = len(message).to_bytes(4, "little") + bytes(message.encode())
        return self.send_bytes(message_bytes)

    def close(self):
        self.client.close()
