import bpy
from bpy.types import Operator
from .simulator import Simulator


class SIMENV_OT_ImportScene(Operator):
    bl_idname = "simenv.import_scene"
    bl_label = "Import Scene"
    bl_description = "Import a scene from the SimEnv library through TCP"

    @classmethod
    def poll(cls, context) -> bool:
        return True

    def execute(self, context):
        simulator = Simulator()
        return {'FINISHED'}
