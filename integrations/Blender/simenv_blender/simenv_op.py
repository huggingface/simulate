from bpy.types import Operator

from .simulator import Simulator


class SIMULATE_OT_ImportScene(Operator):
    bl_idname = "simulate.import_scene"
    bl_label = "Import Scene"
    bl_description = "Import a scene from the Simulate library through TCP"

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        _ = Simulator()
        return {"FINISHED"}
