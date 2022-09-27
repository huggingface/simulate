import base64
import json
import os
from pathlib import Path

import bpy

from .client import Client


class Simulator:
    def __init__(self):
        self.client = Client()
        self.client.listen(self.dispatch_command)

    def dispatch_command(self, data):
        json_data = json.loads(data)
        getattr(self, json_data["type"])(json_data["contents"])

    def build_scene(self, data):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

        gltf_data = base64.b64decode(data["b64bytes"].encode("ascii"))
        with open("tmp_scene.glb", "wb") as f:
            f.write(gltf_data)

        bpy.ops.import_scene.gltf(filepath="tmp_scene.glb")
        os.remove("tmp_scene.glb")
        self._callback("{}")
        self.client.listen(self.dispatch_command)

    def update_scene(self, data):
        self._callback("{}")
        self.client.listen(self.dispatch_command)

    def render(self, data):
        render_count = 0
        if not os.path.isdir(data["path"]):
            os.mkdir(data["path"])

        if len(os.listdir(data["path"])) > 0:
            render_count = max([int(Path(filename).stem) for filename in os.listdir(data["path"])]) + 1

        bpy.context.scene.render.engine = "CYCLES"
        for scene in bpy.data.scenes:
            scene.cycles.device = "GPU"

        bpy.context.scene.camera = bpy.data.objects.get("cam1")
        bpy.context.scene.render.filepath = os.path.join(data["path"], str(render_count) + ".png")
        bpy.ops.render.render(write_still=True)
        self._callback("{}")
        self.client.listen(self.dispatch_command)

    def close(self, data):
        self._callback("{}")
        self.client.close()

    def _callback(self, data):
        self.client.send_bytes(len(data).to_bytes(4, "little") + data.encode())
