class_name HFActuator
extends Node3D


var action_mapping: ActionMapping
var action_space: ActionSpace
var n: int
var dtype: String
var low: Array
var high: Array
var shape: Array 
var actuator_tag: String
var is_actor: bool


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	var actuator: Dictionary = state.json["extensions"]["HF_actuators"]["objects"][extensions["HF_actuators"]["object_id"]]
	action_space = ActionSpace.new()
	name = extensions["HF_actuators"]["name"]
	
	if json.has("extras"):
		is_actor = json["extras"].get("is_actor", false)
	
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
	
	for key in actuator.keys():
		match key:
			"mapping":
				for mapping in actuator["mapping"]:
					action_mapping = ActionMapping.new()
					for mapping_key in mapping.keys():
						match mapping_key:
							"action":
								action_mapping.action = mapping["action"]
							"amplitude":
								action_mapping.amplitude = mapping["amplitude"]
							"offset":
								action_mapping.offset = mapping["offset"]
							"axis":
								action_mapping.axis = Vector3(
									mapping["axis"][0], 
									mapping["axis"][1], 
									mapping["axis"][2],
								)
							"position":
								action_mapping.position = Vector3(
									mapping["position"][0],
									mapping["position"][1], 
									mapping["position"][2],
								)
							"use_local_coordinates":
								action_mapping.use_local_coordinates = mapping["use_local_coordinates"]
							"is_impulse":
								action_mapping.is_impulse = mapping["is_impulse"]
							"max_velocity_threshold":
								action_mapping.max_velocity_threshold = mapping["max_velocity_threshold"]
					action_space.action_map.append(action_mapping)
			"n":
				n = actuator["n"]
			"dtype":
				dtype = actuator["dtype"]
			"low":
				low = actuator["low"]
			"high":
				high = actuator["high"]
			"shape":
				shape = actuator["shape"]
			"actuator_tag":
				actuator_tag = actuator["actuator_tag"]
			_:
				print("Field not implemented: ", key)


class ActionMapping:
	var action: String
	var amplitude: float = 1.0
	var offset: float = 0.0
	var axis: Vector3
	var position: Vector3
	var use_local_coordinates: bool = true
	var is_impulse: bool = false
	var max_velocity_threshold: float


class ActionSpace:
	var action_map: Array

	func _init():
		self.action_map = []

	func get_mapping(key) -> ActionMapping:
		var index: int = int(key)
		return self.action_map[index]
