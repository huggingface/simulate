extends Node3D
class_name HFRaycastSensor


var n_horizontal_rays: int
var n_vertical_rays: int
var horizontal_fov: float
var vertical_fov: float
var ray_length: float
var sensor_tag: String


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	print("Importing a raycast sensor.")
	var raycast_sensor: Dictionary = state.json["extensions"]["HF_raycast_sensors"]["objects"][extensions["HF_raycast_sensors"]["object_id"]]
	name = extensions["HF_raycast_sensors"]["name"]
	
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
	
	for key in raycast_sensor.keys():
		match key:
			"n_horizontal_rays":
				n_horizontal_rays = raycast_sensor["n_horizontal_rays"]
			"n_vertical_rays":
				n_vertical_rays = raycast_sensor["n_vertical_rays"]
			"horizontal_fov":
				horizontal_fov = raycast_sensor["horizontal_fov"]
			"vertical_fov":
				vertical_fov = raycast_sensor["vertical_fov"]
			"ray_length":
				ray_length = raycast_sensor["ray_length"]
			"sensor_tag":
				sensor_tag = raycast_sensor["sensor_tag"]
			_:
				print("Field not implemented: ", key)
