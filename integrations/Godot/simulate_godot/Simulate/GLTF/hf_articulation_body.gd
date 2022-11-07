extends Generic6DOFJoint3D
class_name HFArticulationBody


var joint_type: String = ""
var anchor_rotation: Quaternion = Quaternion.IDENTITY
var anchor_position: Vector3 = Vector3.ZERO
var inertia_tensor: Vector3
var immovable: bool = false
var linear_damping: float = 0.0
var angular_damping: float = 0.0
var joint_friction: float = 0.0
var drive_stiffness: float = 0.0
var drive_damping: float = 0.0
var drive_force_limit: float = 0.0
var drive_target: float = 0.0
var drive_target_velocity: float = 0.0
var is_limited: bool = false
var upper_limit: float = 0.0
var lower_limit: float = 0.0
var mass: float = 1.0
var center_of_mass: Vector3 = Vector3.ZERO


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	print("Importing an articulation body.")
	var articulation_body: Dictionary = state.json["extensions"]["HF_articulation_bodies"]["objects"][extensions["HF_articulation_bodies"]["object_id"]]
	name = extensions["HF_articulation_bodies"]["name"]
	
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
	
	for key in articulation_body.keys():
		match key:
			"joint_type":
				joint_type = articulation_body["joint_type"]
			"anchor_rotation":
				anchor_rotation = Quaternion(
					articulation_body["anchor_rotation"][0],
					articulation_body["anchor_rotation"][1],
					articulation_body["anchor_rotation"][2],
					articulation_body["anchor_rotation"][3],
				)
			"anchor_position":
				anchor_position = Vector3(
					articulation_body["anchor_position"][0],
					articulation_body["anchor_position"][1],
					articulation_body["anchor_position"][2],
				)
			"inertia_tensor":
				inertia_tensor = Vector3(
					articulation_body["inertia_tensor"][0],
					articulation_body["inertia_tensor"][1],
					articulation_body["inertia_tensor"][2],
				)
			"immovable":
				immovable = articulation_body["immovable"]
			"linear_damping":
				linear_damping = articulation_body["linear_damping"]
			"angular_damping":
				angular_damping = articulation_body["angular_damping"]
			"joint_friction":
				joint_friction = articulation_body["joint_friction"]
			"drive_stiffness":
				drive_stiffness = articulation_body["drive_stiffness"]
			"drive_damping":
				drive_damping = articulation_body["drive_damping"]
			"drive_force_limit":
				drive_force_limit = articulation_body["drive_force_limit"]
			"drive_target":
				drive_target = articulation_body["drive_target"]
			"drive_target_velocity":
				drive_target_velocity = articulation_body["drive_target_velocity"]
			"is_limited":
				is_limited = articulation_body["is_limited"]
			"upper_limit":
				upper_limit = articulation_body["upper_limit"]
			"lower_limit":
				lower_limit = articulation_body["lower_limit"]
			_:
				print("Field not implemented: ", key)
