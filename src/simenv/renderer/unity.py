import json
import socket
import uuid


PRIMITIVE_TYPE_MAPPING = {
    "Sphere": 0,
    "Capsule": 1,
    "Cylinder": 2,
    "Cube": 3,
    "Plane": 4,
    "Quad": 5,
}

class Unity:
    def __init__(self, scene):
        self.scene = scene
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
        contents_dict = {
                "name": node.name,
                "id": str(uuid.uuid4()),
                "pos": node.translation,
                "rot": node.rotation,
                "scale": node.scale,
            }
        node_class = node.__class__.__name__

        if node_class == "Camera":
            command_type = "CreateCamera"
            contents_dict.update({
                        "width": node.width,
                        "height": node.height,
                    })
        elif node_class == "Light":
            command_type = "CreateLight"
            contents_dict.update({
                        "type": node.type,
                        "intensity": node.intensity,
                    })
        elif node_class == "Agent":
            command_type = "CreateAgent"
        elif node_class in PRIMITIVE_TYPE_MAPPING:
            command_type = "CreatePrimitive"
            contents_dict.update({
                        "primitiveType": PRIMITIVE_TYPE_MAPPING[node.__class__.__name__],
                        "dynamic": node.dynamic,
                    })
        else:
            raise "node type not implemented"

        command = {
            "type": command_type,
            "contents": json.dumps(contents_dict),
        }
        self.run_command(command)

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
