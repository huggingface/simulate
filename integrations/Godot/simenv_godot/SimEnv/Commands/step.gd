extends Node
# Step through the simulation (also steps the physics!)


signal callback


func execute(_content):
	get_tree().paused = false
	emit_signal("callback", PackedByteArray([97, 99, 107]))
