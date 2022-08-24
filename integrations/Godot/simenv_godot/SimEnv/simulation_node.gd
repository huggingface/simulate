class_name SimulationNode
extends Node3D


var camera_data
var light_data
var collider_data
var rigidbody_data
var joint_data
var agent_data

var camera
var light
var collider
var rigidbody
var joint
var data


func initialize() -> void:
	pass

func reset_state() -> void:
	pass

func initialize_camera() -> void:
	pass

func initiliaze_light() -> void:
	pass

func initialize_collider() -> void:
	pass

func initialize_rigidbody() -> void:
	pass

func initialize_joint() -> void:
	pass

func get_data():
	pass


class Data:
	var name: String
	var position: Vector3
	var rotation: Quaternion
