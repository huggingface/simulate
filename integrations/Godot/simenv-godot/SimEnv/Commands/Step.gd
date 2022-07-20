extends Node
# Handles the stepping of the simulation
# Unpause the application to run a step of _physics_process

signal callback


func execute(_content):
	get_tree().paused = false
	emit_signal("callback", PackedByteArray([97, 99, 107]))
