extends PhysicsMaterial
class_name HFPhysicMaterial


var material_name: String = ""
var dynamic_friction: float = 0.6
var friction_combine: GLTFEnums.PhysicMaterialCombine
var bounce_combine: GLTFEnums.PhysicMaterialCombine


func import(state: GLTFState, extensions: Dictionary, id: int):
	print("Importing a physic material.")
	var physic_material: Dictionary = state.json["extensions"]["HF_physic_materials"]["objects"][id]
	material_name = extensions["HF_physic_materials"]["name"]
	friction = 0.6
	
	for key in physic_material.keys():
		match key:
			"name":
				material_name = physic_material["name"]
			"dynamic_friction":
				dynamic_friction = physic_material["dynamic_friction"]
			"static_friction":
				friction = physic_material["static_friction"]
			"bounciness":
				bounce = physic_material["bounciness"]
			"friction_combine":
				friction_combine = GLTFEnums.PhysicMaterialCombine.get(physic_material["friction_combine"])
			"bounce_combine":
				bounce_combine = GLTFEnums.PhysicMaterialCombine.get(physic_material["bounce_combine"])
			_:
				print("Field not implemented: ", key)
