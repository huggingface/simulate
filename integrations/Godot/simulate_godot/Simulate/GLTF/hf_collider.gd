extends StaticBody3D
class_name HFCollider


var type: GLTFEnums.ColliderType = GLTFEnums.ColliderType.box
var bounding_box: Vector3
var offset: Vector3 = Vector3.ZERO
var intangible: bool = false
var convex: bool = false
var physic_material: HFPhysicMaterial


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	print("Importing a collider.")
	var collider: Dictionary = state.json["extensions"]["HF_colliders"]["objects"][extensions["HF_colliders"]["object_id"]]
	name = extensions["HF_colliders"]["name"]
	
	position = Vector3(
		json["translation"][0], 
		json["translation"][1], 
		json["translation"][2],
	)
	rotation = Quaternion(
		json["rotation"][0],
		json["rotation"][1],
		json["rotation"][2],
		json["rotation"][3],
	).get_euler()
	scale = Vector3(
		json["scale"][0],
		json["scale"][1],
		json["scale"][2],
	)
	
	for key in collider.keys():
		match key:
			"name":
				name = collider["name"]
			"type":
				type = GLTFEnums.ColliderType.get(collider["type"])
			"bounding_box":
				bounding_box = Vector3(
					collider["bounding_box"][0],
					collider["bounding_box"][1],
					collider["bounding_box"][2],
				)
			"offset":
				offset = Vector3(
					collider["offset"][0],
					collider["offset"][1],
					collider["offset"][2],
				)
			"intangible":
				intangible = collider["intangible"]
			"convex":
				convex = collider["convex"]
			"physic_material":
				physic_material = HFPhysicMaterial.new()
				physic_material.import(state, extensions, collider["physic_material"])
			_:
				print("Field not implemented: ", key)
