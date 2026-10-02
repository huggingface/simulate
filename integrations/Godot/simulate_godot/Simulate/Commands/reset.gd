extends Node
# Reset the simulation


func execute(_content: Variant) -> void:
	Simulator.get_tree().paused = false
	Simulator.send_callback("{}")
