class_name Actor
extends Node3D


var node: Node3D
var sensors: Array
var observations: Dictionary
var actuators: Dictionary
var reward_functions: Array
var accum_reward: float
var current_action: Dictionary


func _init(actor_node: Node):
	node = actor_node
	initialize()


func initialize() -> void:
	for child in Simulator.get_all_children(node):
		if child is HFActuator:
			actuators[child.actuator_tag] = child
		if child is Camera3D or child is HFStateSensor or child is HFRaycastSensor:
			sensors.append(child)
		if child is HFRewardFunction:
			reward_functions.append(child)


func step(action: Dictionary) -> void:
	current_action = action
	var action_value = current_action.get("actuator")


func enable_sensors():
	for sensor in sensors:
		sensor.enable()


func disable_sensors():
	for sensor in sensors:
		sensor.disable()


func get_sensor_observations() -> Dictionary:
	return {}


func update_reward() -> void:
	accum_reward += calculate_reward()


func reset() -> void:
	accum_reward = 0.0
	for reward_function in reward_functions:
		reward_function.reset()


func calculate_reward() -> float:
	var reward = 0.0
	for reward_function in reward_functions:
		reward += reward_function.calculate_reward()
	return reward


func get_reward() -> float:
	return accum_reward


func zero_reward() -> void:
	accum_reward = 0.0


func is_done() -> bool:
	var done = false
	return done


class Data:
	var done: bool
	var reward: float
	var frames: Dictionary
