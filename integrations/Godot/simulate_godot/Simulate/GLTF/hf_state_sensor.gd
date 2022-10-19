extends Node3D
class_name HFStateSensor


var reference_entity: String
var target_entity:String
var properties: Array
var sensor_tag: String


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	print("Importing a state sensor.")
	var state_sensor: Dictionary = state.json["extensions"]["HF_state_sensors"]["objects"][extensions["HF_state_sensors"]["object_id"]]
	name = extensions["HF_state_sensors"]["name"]
	
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
	
	for key in state_sensor.keys():
		match key:
			"target_entity":
				target_entity = state_sensor["target_entity"]
			"reference_entity":
				reference_entity = state_sensor["reference_entity"]
			"properties":
				properties = state_sensor["properties"]
			"sensor_tag":
				sensor_tag = state_sensor["sensor_tag"]
			_:
				print("Field not implemented: ", key)
