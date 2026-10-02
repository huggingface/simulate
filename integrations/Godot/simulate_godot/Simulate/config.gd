extends Node


var time_step: float = 0.02
var frame_skip: int = 1
var return_nodes: bool = true
var return_frames: bool = true
var node_filter: Array
var camera_filter: Array
var ambient_color: Color = Color.GRAY
var gravity: Vector3 = Vector3.DOWN * 9.81


func parse(config: Dictionary):
	time_step = config.get("time_step", 0.02)
	frame_skip = config.get("frame_skip", 1)
	return_nodes = config.get("return_nodes", true)
	return_frames = config.get("return_frames", true)
	node_filter = config.get("node_filter", [])
	camera_filter = config.get("camera_filter", [])
	var color_array = config.get("ambient_color")
	if color_array:
		ambient_color = Color(color_array[0], color_array[1], color_array[2])
	else:
		ambient_color = Color.GRAY
	var gravity_array = config.get("gravity")
	if gravity_array:
		gravity = Vector3(gravity_array[0], gravity[1], gravity[2])
	else:
		gravity = Vector3.DOWN * 9.81
