class_name HFRigidBody
extends RigidBody3D


var constraints: Array
var actuator: HFActuator


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	var rigid_body: Dictionary = state.json["extensions"]["HF_rigid_bodies"]["objects"][extensions["HF_rigid_bodies"]["object_id"]]
	name = json["name"]

	var mesh = MeshInstance3D.new()
	mesh.mesh = state.meshes[json["mesh"]].mesh.get_mesh()
	mesh.name = json["name"] + "_mesh"
	add_child(mesh)
	
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
	
	for key in rigid_body.keys():
		match key:
			"name":
				name = rigid_body["name"]
			"mass":
				mass = rigid_body["mass"]
			"center_of_mass":
				center_of_mass = Vector3(
					rigid_body["center_of_mass"][0],
					rigid_body["center_of_mass"][1],
					rigid_body["center_of_mass"][2],
				)
			"inertia_tensor":
				inertia = Vector3(
					rigid_body["inertia_tensor"][0],
					rigid_body["inertia_tensor"][1],
					rigid_body["inertia_tensor"][2],
				)
			"linear_drag":
				linear_damp = rigid_body["linear_drag"]
			"angular_drag":
				angular_damp = rigid_body["angular_drag"]
			"constraints":
				constraints = rigid_body["constraints"]
			"use_gravity":
				gravity_scale = float(rigid_body["use_gravity"])
			"collision_detection":
				continuous_cd = rigid_body["collision_detection"] == "continuous"
			"kinematic":
				custom_integrator = rigid_body["kinematic"]
			_:
				print("Field not implemented: ", key)
