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

    def send_buffer(self, name, bytes):
        print(f"Sending buffer {name} with length: {len(bytes)}")
        command = {"type": "BeginTransferBuffer", "contents": json.dumps({"name": name, "length": len(bytes)})}
        self.run_command(command)
        print(f"Sending bytes with length {len(bytes)}")
        self.send_bytes(bytes)

    def send_gltf(self, files: dict):
        for key in files.keys():
            if key == "model.gltf":
                continue
            self.send_buffer(key, files[key])
        gltf = files["model.gltf"]
        command = {"type": "ConstructScene", "contents": json.dumps({"json": gltf.decode()})}
        self.run_command(command)

    def run_command(self, command):
        message = json.dumps(command)
        print("Sending command: " + message)
        self.send_bytes(message.encode())

    def close(self):
        self.client.close()
