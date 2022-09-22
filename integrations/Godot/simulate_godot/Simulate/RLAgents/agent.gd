class_name Agent
extends Node


var node: SimulationNode
var action_space
var observations
var reward_functions
var accum_reward: float
var current_action


func _init(node: SimulationNode):
	self.node = node

func initialize() -> void:
	pass

func handle_intermediate_frame() -> void:
	pass

func step(action) -> void:
	pass

func get_event_data() -> Data:
	return Data.new()

func agent_update() -> void:
	pass

func get_camera_observations() -> Dictionary:
	return {}

func update_reward() -> void:
	pass

func reset() -> void:
	pass

func calculate_reward() -> float:
	return 0.0

func get_reward() -> float:
	return 0.0

func zero_reward() -> float:
	return 0.0

func is_done() -> bool:
	return false

func try_get_reward_function(reward, reward_function) -> bool:
	return true


class Data:
	var done: bool
	var reward: float
	var frames: Dictionary
