extends Node3D
class_name HFRewardFunction


var type: String
var entity_a: String
var entity_b: String
var distance_metric: String
var direction: Vector3
var scalar: float
var threshold: float
var is_terminal: bool
var is_collectable: bool
var trigger_once: bool


func import(state: GLTFState, json: Dictionary, extensions: Dictionary):
	print("Importing a reward function.")
	var reward_function: Dictionary = state.json["extensions"]["HF_reward_functions"]["objects"][extensions["HF_reward_functions"]["object_id"]]
	name = extensions["HF_reward_functions"]["name"]
	
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
	
	for key in reward_function.keys():
		match key:
			"type":
				type = reward_function["type"]
			"entity_a":
				entity_a = reward_function["entity_a"]
			"entity_b":
				entity_b = reward_function["entity_b"]
			"distance_metric":
				distance_metric = reward_function["distance_metric"]
			"direction":
				direction = Vector3(
					reward_function["direction"][0],
					reward_function["direction"][1],
					reward_function["direction"][2],
				)
			"scalar":
				scalar = reward_function["scalar"]
			"threshold":
				threshold = reward_function["threshold"]
			"is_terminal":
				is_terminal = reward_function["is_terminal"]
			"is_collectable":
				is_collectable = reward_function["is_collectable"]
			"trigger_once":
				trigger_once = reward_function["trigger_once"]
			_:
				print("Field not implemented: ", key)
