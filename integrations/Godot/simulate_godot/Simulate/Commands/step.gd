extends Node
# Step through the simulation (also steps the physics!)


var frame_skip: int
var time_step: float
var return_frames: bool
var return_nodes: bool


func execute(content: Variant) -> void:
	if content.get("frame_skip", 1):
		Simulator.get_tree().paused = false
	if content.has("action"):
		for actor in Simulator.actors:
			actor.step(content.get("action"))
	var event_data = {
		"actor_sensor_buffers": {
			"raycast_sensor": {
				"type": "float",
				"shape": [1, 1, 4],
				"floatBuffer": [0.0, 0.0, 0.0, 0.0]
			}
		},
		"actor_reward_buffer": {
			"type": "float",
			"shape": 1,
			"floatBuffer": [0.0]
		},
		"actor_done_buffer": {
			"type": "uint8",
			"shape": 1,
			"uintBuffer": [0]
		}
	}
	Simulator.send_callback(str(event_data))
