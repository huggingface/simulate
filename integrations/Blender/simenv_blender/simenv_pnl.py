from bpy.types import Panel


class SIMULATE_PT_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Simulation Environment"
    bl_category = "Simulation"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Simulation Environment")
        row = layout.row()
        row.operator("simulate.import_scene", text="Import Scene")
