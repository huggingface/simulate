import simenv as sm
import trimesh
from trimesh.exchange.gltf import export_gltf
import socket
import json


class Scene():
    def __init__(self, frame_rate=24):
        self.frame_rate = frame_rate
        self.nodes = []

    def add(self, node):
        self.nodes.append(node)

    def __iadd__(self, node):
        self.add(node)
        return self

    def remove(self, node):
        self.nodes.remove(node)

    def __isub__(self, node):
        self.remove(node)
        return self

    def run_command(self, command):
        message = json.dumps(command)
        print('Sending command: ' + message)
        self.send_bytes(message.encode())

    def send_bytes(self, bytes):
        self.client.sendall(bytes)
        while True:
            data = self.client.recv(65535)
            if data:
                response = data.decode()
                print(f'Received response: {response}')
                return response

    def send_buffer(self, name, bytes):
        print(f'Sending buffer {name} with length: {len(bytes)}')
        command = {
            'type': 'BeginTransferBuffer',
            'contents': json.dumps({
                'name': name,
                'length': len(bytes)
            })
        }
        self.run_command(command)
        print(f'Sending bytes with length {len(bytes)}')
        self.send_bytes(bytes)

    def initialize_unity_backend(self):
        self.host = '127.0.0.1'
        self.port = 55000
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        print('Server started. Waiting for connection...')
        self.socket.listen()
        self.client, self.client_address = self.socket.accept()
        print(f'Connection from {self.client_address}')
        files = self.to_gltf()
        for key in files.keys():
            if key == 'model.gltf':
                continue
            self.send_buffer(key, files[key])
        gltf = files['model.gltf']
        command = {
            'type': 'ConstructScene',
            'contents': json.dumps({
                'json': gltf.decode()
            })
        }
        self.run_command(command)

    def to_gltf(self):
        trimesh_scene = trimesh.Scene()
        for node in self.nodes:
            if isinstance(node, sm.Primitive):
                geometry = None
                if node.primitive_type == 0:  # sphere
                    geometry = trimesh.creation.uv_sphere()
                elif node.primitive_type == 1:  # capsule
                    geometry = trimesh.creation.capsule()
                elif node.primitive_type == 2:  # cylinder
                    geometry = trimesh.creation.cylinder(1)
                elif node.primitive_type == 3:  # cube
                    geometry = trimesh.creation.box()
                else:
                    print(f'Primitive type {node.primitive_type} not implemented for Trimesh view')
                if geometry is not None:
                    trimesh_scene.add_geometry(geometry=geometry)
        return export_gltf(trimesh_scene)
