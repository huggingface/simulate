import json
import socket
import uuid

import simenv as sm
from simenv import core


class Unity(core.View):
    def __init__(self, scene):
        super().__init__(scene)
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
        command = {
            "type": "Initialize",
            "contents": json.dumps(
                {
                    "startFrame": self.scene.start_frame,
                    "endFrame": self.scene.end_frame,
                    "frameRate": self.scene.frame_rate,
                }
            ),
        }
        self.run_command(command)

    def step(self):
        command = {"type": "Step", "contents": "{}"}
        self.run_command(command)

    def run(self):
        command = {"type": "Run", "contents": "{}"}
        self.run_command(command)

    def render(self, dirpath):
        command = {"type": "Render", "contents": json.dumps({"dirpath": dirpath})}
        self.run_command(command)

    def add(self, node):
        super().add(node)
        if isinstance(node, sm.Camera):
            command = {
                "type": "CreateCamera",
                "contents": json.dumps(
                    {
                        "name": node.name,
                        "id": str(uuid.uuid4()),
                        "pos": node.translation,
                        "rot": node.rotation,
                        "scale": node.scale,
                        "width": node.width,
                        "height": node.height,
                    }
                ),
            }
            self.run_command(command)
        elif isinstance(node, sm.Light):
            command = {
                "type": "CreateLight",
                "contents": json.dumps(
                    {
                        "name": node.name,
                        "id": str(uuid.uuid4()),
                        "pos": node.translation,
                        "rot": node.rotation,
                        "scale": node.scale,
                        "type": node.type,
                        "intensity": node.intensity,
                    }
                ),
            }
            self.run_command(command)
        elif isinstance(node, sm.Agent):
            command = {
                "type": "CreateAgent",
                "contents": json.dumps(
                    {
                        "name": node.name,
                        "id": str(uuid.uuid4()),
                        "pos": node.translation,
                        "rot": node.rotation,
                        "scale": node.scale,
                    }
                ),
            }
            self.run_command(command)
        elif isinstance(node, sm.Primitive):
            command = {
                "type": "CreatePrimitive",
                "contents": json.dumps(
                    {
                        "name": node.name,
                        "id": str(uuid.uuid4()),
                        "pos": node.translation,
                        "rot": node.rotation,
                        "scale": node.scale,
                        "primitiveType": node.primitive_type,
                        "dynamic": node.dynamic,
                    }
                ),
            }
            self.run_command(command)
        else:
            raise "node type not implemented"

    def run_command(self, command):
        message = json.dumps(command)
        return self.send_message(message)

    def send_message(self, message):
        print(f"Sending message: {message}")
        self.client.sendall(message.encode())
        while True:
            data = self.client.recv(65535)
            if data:
                response = data.decode()
                print(f"Received response: {response}")
                return response

    def remove(self, node):
        super().remove(node)

    def close(self):
        self.client.close()
